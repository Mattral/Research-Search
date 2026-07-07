# Hybrid Recommendation Engine

Re‑Search replaces the old, hard‑to‑run Neo4j graph recommender with a **hybrid
engine that has no graph‑database dependency**. It blends three signals into a
single, explainable score.

## Signals & scoring

| Signal | Weight | Source |
|--------|:------:|--------|
| **Semantic similarity** | up to 0.50 | Cosine between the user profile embedding and each paper embedding |
| **Collaborative** (shared authors) | up to 0.25 | Author overlap with papers the user liked/viewed |
| **Field overlap** | 0.10 | Fields of study matching the user's interests/history |
| **Popularity** (citations) | up to 0.15 | `citation_count` (log‑capped) |
| **Recency** | up to 0.10 | Newer papers get a small boost |

Every recommendation ships with human‑readable `reasons`, e.g.
_"Strong semantic match (0.82) to your reading"_, _"Shares 2 author(s) with papers
you've engaged with"_, _"Highly cited (450 citations)"_.

The **user profile embedding** is the mean of: embeddings of the user's
liked/viewed papers (looked up in the corpus) + an embedding of their selected
interests. With no history/interests, the engine falls back to **trending**
(most‑cited) papers.

## Where the data lives

- Papers + embeddings: MongoDB `papers` collection (`db/mongo.py`).
- Similarity: computed in‑process with **numpy** over the seeded corpus
  (small enough that brute‑force cosine is instant). No Atlas `$vectorSearch`
  required.
- Feedback: MongoDB `recommendation_feedback` (thumbs up/down per user+paper).

## Embeddings — key resolution (priority)

1. **`GEMINI_API_KEY`** → native Google Gemini `gemini-embedding-001` (768‑dim).
2. **Fallback** → a deterministic, key‑free **lexical hashing** embedding so the
   app works out‑of‑the‑box.

> The Emergent LLM key powers chat/summaries but does **not** expose a text
> embeddings API, so it is not used for embeddings. Add a `GEMINI_API_KEY` to get
> true semantic embeddings.

> **Free‑tier quota**: Gemini's free tier caps embedding requests at ~1000/day
> (1 request per paper) plus a per‑minute limit. This bounds how large a corpus
> can be (re)seeded per day. Seeding is safe — the existing corpus is only
> replaced after the new embeddings fully succeed — so a quota abort leaves the
> current corpus intact. Use a paid key or the lexical fallback for larger seeds.

## Feedback loop

Thumbs up/down (`POST /api/recommendations/feedback`) are stored per user+paper
in MongoDB and actively shape ranking:
- **Down‑voted** papers are excluded from future recommendations.
- **Up‑voted** papers are added to the user's profile vector, so semantically
  similar work surfaces more often.

`rec_meta` records which backend seeded the corpus. If the active backend later
differs from the seed backend (e.g. the Gemini key was removed), the engine
detects the mismatch and safely returns trending results until re‑seeded.

## Preview vs. Production

| | This preview / managed pod | Production / self‑hosted |
|---|---|---|
| Vector store | MongoDB + in‑process numpy cosine | **pgvector** (recommended) or **MongoDB Atlas `$vectorSearch`** |
| Embeddings | Gemini API (or lexical fallback) | Local `sentence-transformers` (e.g. `all-MiniLM-L6-v2`) or Gemini |
| Why | No docker‑compose / Atlas in the managed pod | Scales to 100k+ papers with ANN indexes |

The scoring logic is identical across both; only the vector query layer differs.
See `ROADMAP.md` (P1) for the pgvector/ANN migration.

## API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/recommendations?limit=` | Personalized hybrid recommendations |
| GET | `/api/recommendations/trending?limit=` | Popularity fallback |
| POST | `/api/recommendations/feedback` | Body `{paper_id, feedback: "up"\|"down", reason?}` |
| GET | `/api/recommendations/status` | Engine, embedding backend, corpus size |

## Seeding the corpus

```bash
cd backend
python -m scripts.seed_papers          # ~1200 papers across default topics
PER_TOPIC=60 python -m scripts.seed_papers   # smaller/faster
```

The script pulls the most‑cited works per topic from OpenAlex, embeds
`title + abstract`, and upserts into MongoDB (idempotent).
