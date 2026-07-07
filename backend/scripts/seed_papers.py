"""
Seed the MongoDB `papers` corpus (with embeddings) for hybrid recommendations.

Primary source: arXiv (reliable, rich abstracts) across research categories.
Bonus source: OpenAlex most-cited works per topic (best-effort; skipped if the
API rate-limits). Embeds title+abstract with the active embedding backend
(Gemini or lexical fallback) and writes to MongoDB. Idempotent full refresh.

Usage (from /app/backend):
    python -m scripts.seed_papers            # ~450 papers
    PER_TOPIC=25 python -m scripts.seed_papers
"""
import os
import sys
import asyncio
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent.parent))

import pymongo
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

from services.arxiv_service import search_arxiv  # noqa: E402
from services.openalex_service import search_openalex  # noqa: E402
from services.embedding_service import embed_texts, active_backend, EMBED_DIM  # noqa: E402

# arXiv category -> field label (aligned with app interest names for overlap)
ARXIV_FIELDS = [
    ("cs.AI", "Artificial Intelligence"),
    ("cs.LG", "Machine Learning"),
    ("stat.ML", "Machine Learning"),
    ("cs.CL", "Natural Language Processing"),
    ("cs.CV", "Computer Vision"),
    ("cs.RO", "Robotics"),
    ("cs.CR", "Cybersecurity"),
    ("cs.IR", "Data Science"),
    ("stat.AP", "Data Science"),
    ("q-bio.GN", "Bioinformatics"),
    ("q-bio.NC", "Neuroscience"),
    ("q-bio.BM", "Bioinformatics"),
    ("quant-ph", "Physics"),
    ("physics.comp-ph", "Physics"),
    ("physics.chem-ph", "Chemistry"),
    ("physics.ao-ph", "Environmental Science"),
    ("math.OC", "Mathematics"),
    ("math.ST", "Mathematics"),
    ("econ.EM", "Economics"),
    ("econ.GN", "Economics"),
    ("eess.IV", "Medicine"),
    ("cs.SE", "Software Engineering"),
    ("cs.DB", "Databases"),
]

OPENALEX_TOPICS = [
    "large language models", "deep learning", "reinforcement learning",
    "graph neural networks",
]


def _arxiv_to_doc(p, field):
    return {
        "source": "arxiv",
        "source_id": p["arxiv_id"],
        "paper_id": p["arxiv_id"],
        "title": p["title"],
        "abstract": p.get("summary") or "",
        "authors": p.get("authors") or [],
        "year": p.get("year"),
        "citation_count": 0,
        "url": p.get("abstract_url") or f"https://arxiv.org/abs/{p['arxiv_id']}",
        "pdf_url": p.get("pdf_url"),
        "doi": p.get("doi"),
        "journal": p.get("journal_ref"),
        "fields_of_study": [field],
    }


def _oa_to_doc(p):
    return {
        "source": "openalex",
        "source_id": p["source_id"],
        "paper_id": p["source_id"],
        "title": p["title"],
        "abstract": p.get("abstract") or "",
        "authors": p.get("authors") or [],
        "year": p.get("year"),
        "citation_count": p.get("citation_count", 0) or 0,
        "url": p.get("url"),
        "pdf_url": p.get("pdf_url"),
        "doi": p.get("doi"),
        "journal": p.get("journal"),
        "fields_of_study": p.get("fields_of_study") or [],
    }


async def main():
    per_topic = int(os.environ.get("PER_TOPIC", "35"))
    client = pymongo.MongoClient(os.environ["MONGO_URL"])
    db = client[os.environ["DB_NAME"]]
    papers = db["papers"]
    meta = db["rec_meta"]
    papers.create_index("paper_id", unique=True)

    seen = set()
    collected = []

    # --- arXiv (primary) ---
    for code, field in ARXIV_FIELDS:
        res = await search_arxiv(query=field, category=code, max_results=per_topic, sort_by="relevance")
        got = 0
        for p in res.get("papers", []):
            pid = p.get("arxiv_id")
            if not pid or pid in seen or not p.get("title"):
                continue
            seen.add(pid)
            collected.append(_arxiv_to_doc(p, field))
            got += 1
        print(f"[seed] arXiv {code} ({field}): +{got} (total {len(collected)})", flush=True)
        await asyncio.sleep(1.0)

    # --- OpenAlex (bonus, best-effort) ---
    for topic in OPENALEX_TOPICS:
        res = await search_openalex(topic, limit=25, sort="cited_by_count:desc")
        got = 0
        for p in res.get("papers", []):
            pid = p.get("source_id")
            if not pid or pid in seen or not p.get("title"):
                continue
            seen.add(pid)
            collected.append(_oa_to_doc(p))
            got += 1
        print(f"[seed] OpenAlex {topic}: +{got} (total {len(collected)})", flush=True)
        await asyncio.sleep(1.0)

    if not collected:
        print("[seed] ABORT: no papers fetched (leaving existing corpus intact).", flush=True)
        return

    texts = [f"{d['title']} . {d.get('abstract', '')}"[:4000] for d in collected]
    print(f"[seed] Embedding {len(texts)} papers via '{active_backend()}' backend ...", flush=True)
    embs = await embed_texts(texts, task_type="retrieval_document")

    ops = []
    for d, e in zip(collected, embs):
        d["embedding"] = e
        ops.append(pymongo.UpdateOne({"paper_id": d["paper_id"]}, {"$set": d}, upsert=True))

    papers.delete_many({})  # clean refresh -> single consistent embedding backend
    papers.bulk_write(ops)

    total = papers.count_documents({})
    meta.update_one(
        {"_id": "papers"},
        {"$set": {
            "_id": "papers",
            "embedding_backend": active_backend(),
            "dim": EMBED_DIM,
            "count": total,
            "seeded_at": datetime.now(timezone.utc).isoformat(),
        }},
        upsert=True,
    )
    print(f"[seed] DONE. corpus={total} backend={active_backend()} dim={EMBED_DIM}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
