# Local Setup

## Prerequisites
- Python 3.11+, Node 18+ / Yarn
- MongoDB running locally (or a connection string)
- (Optional) PostgreSQL — otherwise SQLite is used automatically

## Environment variables

`backend/.env`
```
MONGO_URL=mongodb://localhost:27017
DB_NAME=research_search
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/research_db   # optional; falls back to SQLite
JWT_SECRET=change-me
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
GEMINI_API_KEY=your-gemini-key        # optional: enables Gemini summaries + semantic embeddings
EMERGENT_LLM_KEY=your-emergent-key    # optional: hosted LLM fallback for summaries
# NEO4J_* is optional/legacy and not required
```

`frontend/.env`
```
REACT_APP_BACKEND_URL=http://localhost:8001
```

## Run (managed pod / supervisor)
Services are managed by supervisor and hot‑reload on code changes:
```bash
sudo supervisorctl restart backend
sudo supervisorctl restart frontend
```

## Seed the recommendation corpus
```bash
cd backend
python -m scripts.seed_papers
```

## Quick verification
```bash
API=$REACT_APP_BACKEND_URL
curl $API/api/health
# → {"status":"healthy","recommendation_engine":"hybrid","embedding_backend":"gemini","corpus_size":<n>,...}
```

## Notes on embeddings
- With `GEMINI_API_KEY` set, embeddings use Gemini `gemini-embedding-001` (768‑dim).
- Without it, a key‑free lexical fallback keeps things working (lower quality).
- Re‑run the seed script after changing the embedding backend.
