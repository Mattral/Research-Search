# Roadmap

Living plan for Re‑Search. Status: ✅ done · 🚧 in progress · ⬜ planned.
Priorities follow the Senior Architect refactor playbook (P0 → P1 → P2).

## P0 — Hybrid recommendations, no Neo4j (COMPLETE)
- ✅ MongoDB `papers` corpus + embeddings store (`db/mongo.py`)
- ✅ Embedding service — Gemini (`gemini-embedding-001`) with lexical fallback; key priority `GEMINI_API_KEY` → lexical
- ✅ Hybrid engine — semantic + collaborative (authors) + field overlap + popularity + recency, with explanations
- ✅ Feedback loop — `POST /api/recommendations/feedback` (thumbs up/down, stored in Mongo)
- ✅ Endpoints — `/api/recommendations`, `/trending`, `/feedback`, `/status`
- ✅ Seeding script — `scripts/seed_papers.py` (OpenAlex → embed → upsert)
- ✅ Frontend — `RecommendationCard` with score, reasons, source, feedback; refreshed `RecommendationsPage`
- ✅ Paper detail resolves from Mongo corpus → external APIs (recommendation clicks work end‑to‑end)
- ✅ Removed legacy Neo4j `sys.path` hack + mock legacy rec endpoint
- ✅ Docs: `docs/architecture.md`, `docs/recommendations.md`, `docs/setup.md`

## P1 — Polish, scale, reliability
- ⬜ Settings page: let logged‑in users paste their own `GEMINI_API_KEY` (BYOK), stored per‑user
- ✅ Use stored feedback to boost/penalize future recommendations (down‑vote excludes, up‑vote reinforces profile)
- 🚧 Grow corpus coverage (~23 arXiv categories wired in seed; full ~900‑paper seed pending Gemini daily quota reset / paid key)
- ⬜ Background refresh job to keep corpus fresh (periodic OpenAlex/arXiv ingest + embed)
- ⬜ Caching (frequent rec queries) + retries/backoff + circuit breaker for external APIs
- ⬜ pgvector / Mongo Atlas `$vectorSearch` path for production scale (100k+ papers)
- ⬜ Comprehensive pytest suite (scoring unit tests + engine integration) + CI
- ⬜ Team collaboration: shared workspaces, team tags, shared annotated corpora
- ⬜ BibTeX/Zotero/Mendeley export polish (workspace‑level export UX)

## P2 — Strategic
- ⬜ Optional citation‑network visualization (client‑side graph, e.g. Cytoscape.js)
- ⬜ Multi‑provider AI (local Ollama embeddings/summaries + Gemini fallback, cost tracking)
- ⬜ Learning‑to‑rank / two‑tower personalization
- ⬜ Observability (structured logs, metrics, tracing), feature flags, A/B testing
- ⬜ Plugin architecture for custom sources / rec strategies
- ⬜ CLI interface (`research-search export --papers ids.txt`)
