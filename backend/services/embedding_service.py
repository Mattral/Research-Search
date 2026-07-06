"""
Embedding service for semantic recommendations.

Key resolution priority (per product decision):
  1. GEMINI_API_KEY  -> native Google Gemini text embeddings (gemini-embedding-001)
  2. Fallback        -> local, key-free lexical hashing embedding (always works)

NOTE: The Emergent LLM key powers chat/summaries but does NOT expose a text
embeddings API, so it cannot be used for embeddings. When no working Gemini key
is present we degrade gracefully to a deterministic lexical embedding so the app
keeps functioning out-of-the-box. Setting GEMINI_API_KEY upgrades to true
semantic embeddings. Self-hosted/production can swap this for a local
sentence-transformers model + pgvector (see docs/recommendations.md).
"""
import os
import re
import hashlib
import asyncio
import logging
from pathlib import Path

import numpy as np
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")
logger = logging.getLogger(__name__)

EMBED_DIM = 768
GEMINI_MODEL = "models/gemini-embedding-001"

_gemini_ready = False
_gemini_key = os.environ.get("GEMINI_API_KEY")

if _gemini_key:
    try:
        import google.generativeai as genai
        genai.configure(api_key=_gemini_key)
        _gemini_ready = True
    except Exception as e:  # pragma: no cover
        logger.warning(f"Gemini embeddings unavailable, using lexical fallback: {e}")


def active_backend() -> str:
    return "gemini" if _gemini_ready else "lexical"


def _normalize(vec) -> list:
    a = np.asarray(vec, dtype=np.float32)
    n = np.linalg.norm(a)
    if n > 0:
        a = a / n
    return a.astype(np.float32).tolist()


def _lexical_embed(text: str) -> list:
    """Deterministic, key-free hashing embedding (stable across processes)."""
    vec = np.zeros(EMBED_DIM, dtype=np.float32)
    for tok in re.findall(r"[a-z0-9]+", (text or "").lower()):
        h = int(hashlib.md5(tok.encode()).hexdigest(), 16)
        idx = h % EMBED_DIM
        sign = 1.0 if (h >> 16) & 1 else -1.0
        vec[idx] += sign
    return _normalize(vec)


def _gemini_embed_batch(texts, task_type) -> list:
    import time
    import google.generativeai as genai
    try:
        from google.api_core.exceptions import ResourceExhausted, ServiceUnavailable, DeadlineExceeded
        transient = (ResourceExhausted, ServiceUnavailable, DeadlineExceeded)
    except Exception:
        transient = tuple()

    last_err = None
    for attempt in range(6):
        try:
            res = genai.embed_content(
                model=GEMINI_MODEL,
                content=texts,
                task_type=task_type,
                output_dimensionality=EMBED_DIM,
            )
            embs = res["embedding"]
            if texts and not isinstance(embs[0], (list, tuple)):
                embs = [embs]  # single-item responses
            return [_normalize(e) for e in embs]
        except transient as e:
            last_err = e
            delay = min(6 * (attempt + 1), 35)
            logger.warning(f"Gemini embed transient error, retrying in {delay}s (attempt {attempt + 1}/6)")
            time.sleep(delay)
    raise last_err if last_err else RuntimeError("Gemini embedding failed")


async def embed_texts(texts, task_type: str = "retrieval_document") -> list:
    if not texts:
        return []
    if _gemini_ready:
        # Consistent backend only: retry on rate limits, never silently mix in
        # lexical vectors (that would corrupt the shared embedding space).
        # Smaller batches + a short inter-batch pause stay friendly to the
        # Gemini free-tier per-minute limit. NOTE: the free tier also caps
        # embedding requests per DAY (~1000), which bounds how large a corpus
        # can be (re)seeded per day; use a paid key or the lexical fallback to
        # seed larger corpora.
        out = []
        n = len(texts)
        for i in range(0, n, 20):
            out.extend(await asyncio.to_thread(_gemini_embed_batch, texts[i:i + 20], task_type))
            if i + 20 < n:
                await asyncio.sleep(4)
        return out
    return [_lexical_embed(t) for t in texts]


async def embed_query(text: str) -> list:
    res = await embed_texts([text], task_type="retrieval_query")
    return res[0]
