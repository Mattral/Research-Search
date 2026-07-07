# Changelog

All notable changes to Re‑Search are documented here.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

## [2.1.0] — 2026-07-07
### Added
- **Feedback‑aware ranking**: stored thumbs feedback now shapes results —
  down‑voted papers are excluded from future recommendations, and up‑voted
  papers reinforce the user's profile vector (surfacing more like them).
- Broader seed coverage: `scripts/seed_papers.py` now spans ~23 arXiv
  categories mapped to app interests (AI, ML, NLP, CV, Robotics, Security,
  Data Science, Bioinformatics, Neuroscience, Physics, Chemistry, Environmental
  Science, Mathematics, Economics, Medicine, Software Engineering, Databases).
- Embedding throttling (smaller batches + inter‑batch pause) for friendlier
  behavior against Gemini free‑tier limits.

### Notes
- Gemini's **free‑tier embedding quota is ~1000 requests/day** (1 request per
  paper). The active corpus is 430 Gemini‑embedded papers; growing to ~900 is
  deferred until the daily quota resets (or with a paid key / lexical fallback).
  Seeding is safe: the existing corpus is only replaced after new embeddings
  fully succeed.

## [2.0.0] — 2026-07-07
### Added
- **Hybrid recommendation engine** (no Neo4j dependency): semantic vector
  similarity + collaborative (shared authors) + field overlap + popularity +
  recency, with human‑readable explanations for every result.
- **MongoDB store** (`db/mongo.py`) for the `papers` corpus (+ embeddings),
  `recommendation_feedback`, and `rec_meta`.
- **Embedding service** (`services/embedding_service.py`): Gemini
  `gemini-embedding-001` (768‑dim) with key priority `GEMINI_API_KEY` →
  deterministic **lexical fallback** (key‑free, works out‑of‑the‑box).
- **Recommendation API**: `GET /api/recommendations`, `/trending`, `/status`,
  and `POST /api/recommendations/feedback` (thumbs up/down).
- **Corpus seeding script** `scripts/seed_papers.py` (OpenAlex → embed → upsert,
  idempotent).
- **Frontend**: `RecommendationCard` (score badge, reason chips, source, thumbs
  feedback) and a rewritten `RecommendationsPage` with engine status.
- **Docs**: `docs/architecture.md`, `docs/recommendations.md`, `docs/setup.md`,
  plus `ROADMAP.md` and this changelog.
- README now embeds the product UI screenshot.

### Changed
- Paper detail (`GET /api/papers/{id}`) now resolves from the local Mongo corpus
  first, then external APIs (OpenAlex/Semantic Scholar) — so recommendation
  clicks resolve end‑to‑end.
- Legacy `/api/papers/recommendations` kept for backwards compatibility (now
  backed by live multi‑source search).
- `MONGO_URL` / `DB_NAME` added to `backend/.env`.

### Fixed
- OpenAlex service crash when a work's `primary_location.source` is `null`.

### Removed
- Neo4j `sys.path` import hack and the mock legacy `/api/recommendations/{user_id}`
  endpoint. Neo4j is now fully optional/legacy.
