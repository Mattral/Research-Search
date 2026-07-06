"""
Hybrid recommendation engine (no Neo4j).

Combines semantic (vector) similarity, collaborative signals (shared authors /
fields of study), and popularity (citations) + recency into an explainable score.
Papers + embeddings live in MongoDB; cosine similarity is computed in-process
with numpy over the (small) seeded corpus.
"""
from typing import List, Dict, Any, Tuple
from datetime import datetime, timezone
import logging

import numpy as np
from sqlalchemy.orm import Session

from models.user_models import User
from db.mongo import papers_collection, meta_collection, feedback_collection
from services.embedding_service import active_backend

logger = logging.getLogger(__name__)
CURRENT_YEAR = datetime.now(timezone.utc).year

_META_FIELDS = [
    "paper_id", "title", "abstract", "authors", "year", "citation_count",
    "url", "pdf_url", "doi", "journal", "fields_of_study", "source",
]
_PROJECTION = {f: 1 for f in _META_FIELDS}
_PROJECTION["embedding"] = 1

# In-process corpus cache (reloaded when the paper count changes).
_cache: Dict[str, Any] = {"count": -1, "ids": [], "matrix": None, "papers": [], "field_to_idx": {}}


async def _load_corpus():
    count = await papers_collection.count_documents({})
    if count == _cache["count"] and _cache["matrix"] is not None:
        return
    docs = await papers_collection.find({}, _PROJECTION).to_list(length=None)
    ids, mats, papers = [], [], []
    field_to_idx: Dict[str, List[int]] = {}
    for d in docs:
        emb = d.get("embedding")
        if not emb:
            continue
        idx = len(ids)
        ids.append(d["paper_id"])
        mats.append(emb)
        d.pop("_id", None)
        d.pop("embedding", None)
        papers.append(d)
        for f in (d.get("fields_of_study") or []):
            field_to_idx.setdefault(f.lower(), []).append(idx)
    _cache["count"] = count
    _cache["ids"] = ids
    _cache["papers"] = papers
    _cache["matrix"] = np.asarray(mats, dtype=np.float32) if mats else None
    _cache["field_to_idx"] = field_to_idx


def _to_rec(paper: Dict[str, Any], score: float, reasons: List[str], match_type: str) -> Dict[str, Any]:
    return {
        "paper_id": paper.get("paper_id"),
        "title": paper.get("title", ""),
        "score": round(float(score), 3),
        "reasons": reasons,
        "match_type": match_type,
        "authors": paper.get("authors", []) or [],
        "year": paper.get("year"),
        "venue": paper.get("journal"),
        "abstract": (paper.get("abstract") or "")[:600],
        "url": paper.get("url"),
        "pdf_url": paper.get("pdf_url"),
        "doi": paper.get("doi"),
        "source": paper.get("source"),
        "citation_count": paper.get("citation_count") or 0,
        "fields_of_study": paper.get("fields_of_study", []) or [],
    }


def _score(paper: Dict[str, Any], vec_sim: float, hist_authors: set, hist_fields: set) -> Tuple[float, List[str], str]:
    reasons: List[str] = []
    contrib: Dict[str, float] = {}
    score = 0.0

    v = max(0.0, vec_sim) * 0.5
    score += v
    contrib["semantic"] = v
    if vec_sim >= 0.75:
        reasons.append(f"Strong semantic match ({vec_sim:.2f}) to your reading")
    elif vec_sim >= 0.5:
        reasons.append(f"Semantically related ({vec_sim:.2f}) to your interests")

    authors = {a.lower() for a in (paper.get("authors") or [])}
    overlap = len(authors & hist_authors)
    if overlap > 0:
        a = min(overlap / 3.0, 1.0) * 0.25
        score += a
        contrib["author"] = a
        reasons.append(f"Shares {overlap} author(s) with papers you've engaged with")

    fields = {f.lower() for f in (paper.get("fields_of_study") or [])}
    field_overlap = fields & hist_fields
    if field_overlap:
        f = 0.1
        score += f
        contrib["field"] = f
        pretty = ", ".join(sorted(field_overlap)[:2]).title()
        reasons.append(f"In your field: {pretty}")

    cites = paper.get("citation_count") or 0
    if cites > 0:
        c = min(cites / 1000.0, 1.0) * 0.15
        score += c
        contrib["popularity"] = c
        if cites >= 100:
            reasons.append(f"Highly cited ({cites} citations)")

    year = paper.get("year")
    if year:
        age = max(CURRENT_YEAR - int(year), 0)
        score += max(0.0, (5 - age) / 5.0) * 0.1
        if age <= 2:
            reasons.append("Recently published")

    if not reasons:
        reasons.append("Popular in your areas of interest")

    match_type = max(contrib, key=contrib.get) if contrib else "popularity"
    return min(score, 1.0), reasons, match_type


def _seen_ids(user: User) -> set:
    return ({f.paper_id for f in (user.favorites or [])}
            | {v.paper_id for v in (user.recent_views or [])})


async def _feedback_sets(user_id: int):
    """Return (up-voted, down-voted) paper_id sets from stored feedback."""
    docs = await feedback_collection.find({"user_id": user_id}).to_list(length=2000)
    ups = {d["paper_id"] for d in docs if d.get("feedback") == "up"}
    downs = {d["paper_id"] for d in docs if d.get("feedback") == "down"}
    return ups, downs


async def get_trending(db: Session, user: User, limit: int = 12) -> List[Dict[str, Any]]:
    seen = _seen_ids(user)
    _, downs = await _feedback_sets(user.id)
    seen |= downs
    docs = await papers_collection.find(
        {}, {f: 1 for f in _META_FIELDS}
    ).sort("citation_count", -1).limit(limit * 3).to_list(length=limit * 3)
    out = []
    for d in docs:
        if d["paper_id"] in seen:
            continue
        d.pop("_id", None)
        out.append(_to_rec(d, 0.5, ["Trending / highly cited in your fields"], "trending"))
        if len(out) >= limit:
            break
    return out


async def get_hybrid_recommendations(db: Session, user: User, limit: int = 12) -> List[Dict[str, Any]]:
    await _load_corpus()
    if _cache["matrix"] is None or not _cache["ids"]:
        return []

    meta = await meta_collection.find_one({"_id": "papers"})
    if meta and meta.get("embedding_backend") and meta["embedding_backend"] != active_backend():
        logger.warning("Embedding backend mismatch (corpus=%s, active=%s) -> trending",
                       meta.get("embedding_backend"), active_backend())
        return await get_trending(db, user, limit)

    interests = [i.name for i in (user.interests or [])]
    id_to_idx = {pid: i for i, pid in enumerate(_cache["ids"])}
    matrix = _cache["matrix"]
    field_to_idx = _cache["field_to_idx"]

    ups, downs = await _feedback_sets(user.id)
    positive_ids = _seen_ids(user) | ups        # signals used to build the profile
    seen = _seen_ids(user) | ups | downs        # excluded from results

    user_vecs: List[np.ndarray] = []
    hist_authors: set = set()
    hist_fields: set = set()

    for pid in positive_ids:
        idx = id_to_idx.get(pid)
        if idx is not None:
            user_vecs.append(matrix[idx])
            p = _cache["papers"][idx]
            hist_authors |= {a.lower() for a in (p.get("authors") or [])}
            hist_fields |= {f.lower() for f in (p.get("fields_of_study") or [])}

    if interests:
        # Derive an interest vector from the centroid of already-embedded corpus
        # papers in those fields — no per-request embedding API call needed.
        matched = set()
        for name in interests:
            matched.update(field_to_idx.get(name.lower(), []))
        if matched:
            centroid = matrix[list(matched)].mean(axis=0)
            n = np.linalg.norm(centroid)
            if n > 0:
                centroid = centroid / n
            user_vecs.append(centroid.astype(np.float32))
        hist_fields |= {i.lower() for i in interests}

    if not user_vecs:
        return await get_trending(db, user, limit)

    profile = np.mean(np.asarray(user_vecs, dtype=np.float32), axis=0)
    n = np.linalg.norm(profile)
    if n > 0:
        profile = profile / n

    sims = matrix @ profile
    order = np.argsort(-sims)

    recs: List[Dict[str, Any]] = []
    for idx in order:
        pid = _cache["ids"][idx]
        if pid in seen:
            continue
        paper = _cache["papers"][idx]
        score, reasons, match_type = _score(paper, float(sims[idx]), hist_authors, hist_fields)
        recs.append(_to_rec(paper, score, reasons, match_type))
        if len(recs) >= limit * 3:
            break

    recs.sort(key=lambda x: x["score"], reverse=True)
    return recs[:limit]
