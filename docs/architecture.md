# Architecture

Re‑Search is a unified research‑discovery platform. It aggregates multiple open
scholarly APIs, layers AI summarization and an explainable hybrid recommendation
engine on top, and organizes everything into researcher workspaces.

## High‑level diagram

```
                       ┌──────────────────────────────┐
                       │        React frontend         │
                       │  Discover · Compare · Trends  │
                       │  Workspaces · For‑You (recs)  │
                       └───────────────┬──────────────┘
                                       │ REST (/api/*, JWT)
                       ┌───────────────▼──────────────┐
                       │         FastAPI backend        │
                       │  routes/ services/ models/     │
                       └───┬───────────┬───────────┬───┘
      relational (users,   │           │           │   corpus + embeddings +
      workspaces, likes)   │           │           │   recommendation feedback
                 ┌─────────▼──┐  ┌─────▼─────┐  ┌───▼────────┐
                 │ SQLAlchemy │  │  External  │  │  MongoDB   │
                 │ (SQLite/PG)│  │  scholarly │  │  papers /  │
                 └────────────┘  │   APIs*    │  │  feedback  │
                                 └────────────┘  └────────────┘
   * arXiv · Semantic Scholar · OpenAlex        AI: Gemini (summaries + embeddings)
```

Neo4j is **optional/legacy** — the recommendation engine no longer depends on it.

## Data stores

| Store | Holds | Notes |
|-------|-------|-------|
| **SQLAlchemy** (SQLite by default, Postgres via `DATABASE_URL`) | Users, interests, workspaces, favorites, recent views | Source of truth for user/relational data |
| **MongoDB** | `papers` corpus (metadata + embedding), `recommendation_feedback`, `rec_meta` | Powers the hybrid recommender; cosine similarity computed in‑process |
| **External APIs** | Live search/detail (arXiv, Semantic Scholar, OpenAlex) | No keys required |
| **Neo4j** *(optional)* | Legacy citation graph | Degrades gracefully if absent |

## Backend layout

```
backend/
├── db/            postgres.py · mongo.py · neo4j.py (optional)
├── models/        SQLAlchemy models (user_models.py)
├── routes/        auth · users · papers · arxiv · discover · recommendation
├── services/      embedding · hybrid_recommendation · ai · {arxiv,openalex,semantic_scholar}
├── scripts/       seed_papers.py (corpus + embeddings)
└── server.py      app factory, lifespan, router wiring
```

## Key request flows

- **Discover search** → `GET /api/discover/search` fans out to arXiv + Semantic
  Scholar + OpenAlex concurrently and merges results.
- **Paper detail** → `GET /api/papers/{id}` reads the local Mongo corpus first,
  then falls back to OpenAlex/Semantic Scholar (by ID convention: `W…` = OpenAlex).
- **Recommendations** → `GET /api/recommendations` runs the hybrid engine (see
  [recommendations.md](./recommendations.md)).
- **AI summary** → `POST /api/arxiv/summarize` / discover summarize via Gemini.
