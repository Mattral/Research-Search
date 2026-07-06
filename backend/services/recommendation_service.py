"""
Recommendation service.

Personalized paper recommendations built from the relational DB
(user interests + liked/viewed history) combined with live results from the
Semantic Scholar API. No graph database dependency.
"""
from typing import List, Dict, Any
from datetime import datetime, timezone
import asyncio
import logging

from sqlalchemy.orm import Session

from models.user_models import User, UserFavorite, UserRecentView
from services.semantic_scholar_service import search_semantic_scholar
from services.openalex_service import search_openalex

logger = logging.getLogger(__name__)

CURRENT_YEAR = datetime.now(timezone.utc).year

# Fallback topics used when a user has no interests or history yet.
DEFAULT_TOPICS = [
    "large language models",
    "deep learning",
    "reinforcement learning",
]


def _build_query_terms(user: User) -> List[str]:
    """Derive search terms from the user's interests, then recent history."""
    terms: List[str] = [i.name for i in (user.interests or [])]

    if not terms:
        # Fall back to keywords from recently viewed / liked paper titles.
        titles = [v.paper_title for v in (user.recent_views or []) if v.paper_title]
        titles += [f.paper_title for f in (user.favorites or []) if f.paper_title]
        terms = [t for t in titles if t][:3]

    if not terms:
        terms = DEFAULT_TOPICS

    return terms[:3]


def _score_paper(paper: Dict[str, Any], interest_terms: List[str]) -> (float, List[str]):
    """Score a candidate paper on recency, citations, and interest match."""
    score = 0.0
    reasons: List[str] = []

    # Interest match
    text = f"{paper.get('title', '')} {' '.join(paper.get('fields_of_study') or [])}".lower()
    matched = next((t for t in interest_terms if t.lower() in text), None)
    if matched:
        score += 0.4
        reasons.append(f"Matches your interest in {matched}")

    # Citation impact (normalized, capped)
    citations = paper.get("citation_count") or 0
    if citations > 0:
        cit_score = min(citations / 500.0, 1.0) * 0.35
        score += cit_score
        if citations >= 100:
            reasons.append(f"Highly cited ({citations} citations)")

    # Recency
    year = paper.get("year")
    if year:
        age = max(CURRENT_YEAR - int(year), 0)
        recency_score = max(0.0, (5 - age) / 5.0) * 0.25
        score += recency_score
        if age <= 2:
            reasons.append("Recently published")

    if not reasons:
        reasons.append("Related to your research field")

    return round(min(score, 1.0), 2), reasons


async def get_recommendations(db: Session, user: User, limit: int = 10) -> List[Dict[str, Any]]:
    """Generate personalized recommendations from interests + live search."""
    interest_terms = _build_query_terms(user)

    # Papers the user already interacted with (exclude from results).
    seen_ids = {f.paper_id for f in (user.favorites or [])}
    seen_ids |= {v.paper_id for v in (user.recent_views or [])}
    seen_titles = {(f.paper_title or "").lower() for f in (user.favorites or [])}
    seen_titles |= {(v.paper_title or "").lower() for v in (user.recent_views or [])}

    # Fetch candidates concurrently across the derived terms.
    # OpenAlex is the primary source (reliable, no key); Semantic Scholar
    # supplements it but is best-effort (public API is rate-limited).
    tasks = []
    for term in interest_terms:
        tasks.append(search_openalex(term, limit=10, sort="cited_by_count:desc"))
        tasks.append(search_semantic_scholar(term, limit=10))
    results = await asyncio.gather(*tasks, return_exceptions=True)

    candidates: Dict[str, Dict[str, Any]] = {}
    for res in results:
        if isinstance(res, Exception):
            logger.error(f"Recommendation candidate fetch failed: {res}")
            continue
        for p in res.get("papers", []):
            pid = p.get("source_id")
            if not pid or pid in candidates or pid in seen_ids:
                continue
            if (p.get("title") or "").lower() in seen_titles:
                continue
            candidates[pid] = p

    recommendations: List[Dict[str, Any]] = []
    for pid, paper in candidates.items():
        score, reasons = _score_paper(paper, interest_terms)
        recommendations.append({
            "paper_id": pid,
            "title": paper.get("title", ""),
            "score": score,
            "reason": "; ".join(reasons),
            "authors": paper.get("authors", []),
            "year": paper.get("year"),
            "venue": paper.get("journal"),
        })

    recommendations.sort(key=lambda x: x["score"], reverse=True)
    return recommendations[:limit]
