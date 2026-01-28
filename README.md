<div align="center">

# Re**Search** — Research Paper Discovery & Recommendation Platform

**Discover, explore, and organize academic papers with AI-powered insights.**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)](https://react.dev)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.x-008CC1?logo=neo4j)](https://neo4j.com)
[![arXiv](https://img.shields.io/badge/arXiv-API-B31B1B)](https://arxiv.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[Getting Started](#getting-started) · [Features](#features) · [Architecture](#architecture) · [Contributing](CONTRIBUTING.md) · [Docker](#docker--kubernetes)

</div>

---

## What is ReSearch?

**ReSearch** is an open-source research paper discovery platform that combines a graph-based recommendation engine with live arXiv integration and AI-powered paper summarization. It helps researchers, students, and academics cut through the noise and find the papers that matter most to their work.

## Who is this for?

| Persona | How ReSearch helps |
|---|---|
| **Graduate students** | Find papers for literature reviews, track citations, build reading lists |
| **Researchers** | Discover related work via graph-based recommendations, get AI summaries to triage papers fast |
| **Academics & professors** | Monitor new publications in their field, share curated paper lists |
| **Independent learners** | Explore arXiv categories, understand complex papers through AI-generated plain-language summaries |

## Why ReSearch?

Academic paper discovery is broken:

- **arXiv is overwhelming** — thousands of new papers daily, no personalized filtering
- **Citation graphs are invisible** — related work is hidden behind manual searches
- **Reading time is limited** — researchers spend hours triaging papers that may not be relevant

ReSearch solves these problems by combining:

1. **Live arXiv search** with category-based filtering, pagination, and sort options
2. **Graph-based recommendations** using Neo4j to surface papers connected by citations, shared authors, and venues
3. **AI-powered summaries** (Gemini) that distill abstracts into plain-language insights with key points
4. **Personal reading lists** to save, organize, and track papers across sessions

## What problem does this solve?

> *"I spend 2 hours every morning just scanning arXiv titles. Most aren't relevant to my work."*

ReSearch reduces paper triage time from hours to minutes by:
- Showing you **what's new** in your specific categories
- **Recommending** papers based on what you've liked and viewed
- Providing **AI summaries** so you can decide in 30 seconds if a paper is worth reading
- Letting you **save and organize** papers for later deep reading

---

## Features

### Core
- **arXiv Live Search** — Search 2M+ papers by keyword, author, abstract, or category
- **Category Browser** — Browse latest papers across 28+ arXiv categories (CS, Physics, Math, etc.)
- **Paper Detail View** — Full metadata, abstract, PDF link, DOI, BibTeX export
- **AI Paper Summaries** — One-click Gemini-powered summaries with key points and significance
- **Reading List** — Save/unsave papers to your personal library
- **Pagination & Sorting** — Navigate large result sets with relevance/date sorting

### Graph Features (Neo4j)
- **Citation-based recommendations** — Papers cited by papers you've liked
- **Author-based discovery** — More work by authors you follow
- **Venue-based suggestions** — Papers from conferences you read
- **Popularity scoring** — Trending papers in your field

### Platform
- **JWT Authentication** — Secure register/login with bcrypt password hashing
- **Interest Onboarding** — Select research interests for personalized experience
- **Dark Academic Theme** — Minimal, distraction-free UI designed for long reading sessions
- **Responsive Design** — Works on desktop, tablet, and mobile
- **RESTful API** — Full OpenAPI/Swagger documentation at `/docs`

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    React 18 Frontend                     │
│  ArxivSearch · PaperDetail · ReadingList · Recommendations│
│               Tailwind CSS · Dark Theme                  │
└────────────────────────┬─────────────────────────────────┘
                         │ REST / JSON + JWT
                         ▼
┌──────────────────────────────────────────────────────────┐
│                  FastAPI Backend (Python)                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐  │
│  │ Auth API │ │ arXiv API│ │ Paper API│ │ AI Service │  │
│  │ (JWT)    │ │ (search, │ │ (Neo4j   │ │ (Gemini)   │  │
│  │          │ │  save)   │ │  graph)  │ │            │  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬───────┘  │
└───────┼─────────────┼────────────┼────────────┼──────────┘
        │             │            │            │
        ▼             ▼            ▼            ▼
  ┌──────────┐  ┌──────────┐ ┌──────────┐ ┌──────────┐
  │PostgreSQL│  │ arXiv.org│ │  Neo4j   │ │ Gemini   │
  │ /SQLite  │  │ (public  │ │  (graph  │ │ (AI/LLM) │
  │ (users)  │  │  API)    │ │  DB)     │ │          │
  └──────────┘  └──────────┘ └──────────┘ └──────────┘
```

For the full architecture document, see [report/Architecture.md](report/Architecture.md).

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Neo4j 5.x (cloud or local) — optional, graph features degrade gracefully
- Gemini API key or Emergent LLM key — for AI summaries

### 1. Clone the repository

```bash
git clone https://github.com/your-org/research-paper-discovery.git
cd research-paper-discovery
```

### 2. Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env`:

```env
DATABASE_URL=sqlite:///./research.db
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
GEMINI_API_KEY=your-gemini-key
```

Start the backend:

```bash
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

API docs available at `http://localhost:8001/docs`

### 3. Frontend setup

```bash
cd frontend
yarn install
```

Create `frontend/.env`:

```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

Start the frontend:

```bash
yarn start
```

Open `http://localhost:3000` in your browser.

### 4. Create an account

1. Click **Create one** on the login page
2. Fill in your details and register
3. Select your research interests during onboarding
4. Start exploring arXiv papers!

---

## Docker & Kubernetes

### Docker

```bash
# Build and run everything
docker-compose up --build

# Or build individually
docker build -t research-backend -f Dockerfile.backend .
docker build -t research-frontend -f Dockerfile.frontend .
```

See [docker-compose.yml](docker-compose.yml) for the full configuration.

### Kubernetes

Manifests are in the `k8s/` directory:

```bash
# Apply all manifests
kubectl apply -f k8s/

# Or step by step
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/ingress.yaml
```

See [k8s/README.md](k8s/README.md) for full Kubernetes deployment guide.

---

## API Reference

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Create account |
| POST | `/api/auth/login` | Get JWT token |
| GET | `/api/auth/me` | Get current user |
| PUT | `/api/auth/me` | Update profile |
| POST | `/api/auth/change-password` | Change password |

### arXiv Integration

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/arxiv/search` | Search arXiv papers |
| GET | `/api/arxiv/categories` | List arXiv categories |
| GET | `/api/arxiv/latest` | Get latest papers by category |
| GET | `/api/arxiv/paper/{id}` | Get paper details |
| POST | `/api/arxiv/summarize` | AI-powered paper summary |
| POST | `/api/arxiv/save` | Save to reading list |
| DELETE | `/api/arxiv/save/{id}` | Remove from reading list |
| GET | `/api/arxiv/reading-list` | Get saved papers |

### Graph Papers (Neo4j)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/papers/search` | Search graph papers |
| GET | `/api/papers/browse` | Browse all papers |
| GET | `/api/papers/recommendations` | Personalized recommendations |
| GET | `/api/papers/{id}` | Paper details with citations |
| POST | `/api/papers/{id}/like` | Like a paper |
| POST | `/api/papers/{id}/view` | Track paper view |

Full interactive API docs: `http://localhost:8001/docs`

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | React 18, Tailwind CSS | UI with dark academic theme |
| Backend | FastAPI, Python 3.11 | REST API, business logic |
| Auth | JWT + bcrypt | Stateless authentication |
| SQL Database | PostgreSQL / SQLite | Users, favorites, reading lists |
| Graph Database | Neo4j | Paper relationships, recommendations |
| External API | arXiv API | Live paper search and metadata |
| AI/LLM | Google Gemini | Paper summarization |
| Containerization | Docker, Kubernetes | Deployment and orchestration |

---

## Project Structure

```
research-paper-discovery/
├── backend/
│   ├── db/                  # Database connections (PostgreSQL, Neo4j)
│   ├── models/              # SQLAlchemy models
│   ├── routes/              # API route handlers
│   │   ├── auth_routes.py   # Authentication endpoints
│   │   ├── arxiv_routes.py  # arXiv integration endpoints
│   │   ├── paper_routes.py  # Graph paper endpoints
│   │   └── user_routes.py   # User management endpoints
│   ├── schemas/             # Pydantic request/response models
│   ├── services/            # Business logic
│   │   ├── arxiv_service.py # arXiv API client & XML parser
│   │   ├── ai_service.py    # Gemini AI summarization
│   │   ├── auth_service.py  # JWT authentication
│   │   └── paper_service.py # Neo4j paper queries
│   ├── server.py            # FastAPI application entry point
│   ├── requirements.txt     # Python dependencies
│   └── .env                 # Environment variables
├── frontend/
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── hooks/           # React hooks (auth)
│   │   ├── lib/             # API client, utilities
│   │   ├── pages/           # Page components
│   │   │   ├── ArxivSearchPage.jsx
│   │   │   ├── ArxivPaperPage.jsx
│   │   │   ├── LatestPapersPage.jsx
│   │   │   ├── ReadingListPage.jsx
│   │   │   └── ...
│   │   └── App.js           # Main app with routing
│   └── package.json
├── recommendation/          # Graph recommendation engine
├── k8s/                     # Kubernetes manifests
├── report/                  # Architecture documentation
├── CONTRIBUTING.md          # Contributor guidelines
├── CODE_OF_CONDUCT.md       # Community standards
├── docker-compose.yml       # Docker orchestration
├── Dockerfile.backend       # Backend container
├── Dockerfile.frontend      # Frontend container
└── README.md                # This file
```

---

## How it benefits users

| Benefit | How |
|---------|-----|
| **Save time** | AI summaries let you triage papers in 30 seconds instead of 10 minutes |
| **Discover more** | Graph recommendations surface papers you'd never find through keyword search |
| **Stay current** | Latest papers feed keeps you up-to-date with daily arXiv submissions |
| **Stay organized** | Reading list persists across sessions so you never lose track of a paper |
| **Export easily** | One-click BibTeX export for citations |
| **Privacy-first** | Self-hostable, your reading history stays on your infrastructure |

---

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:

- Setting up your development environment
- Code style and conventions
- Submitting pull requests
- Reporting bugs and requesting features

---

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

---

## Acknowledgements

- [arXiv.org](https://arxiv.org) for the open API providing access to 2M+ research papers
- [Neo4j](https://neo4j.com) for the graph database powering recommendations
- [Google Gemini](https://deepmind.google/technologies/gemini/) for AI-powered paper summaries

---

<div align="center">

**Built for researchers, by researchers.**

[Report Bug](../../issues) · [Request Feature](../../issues) · [Contribute](CONTRIBUTING.md)

</div>
