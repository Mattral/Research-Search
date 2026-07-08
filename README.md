<div align="center">

# Re**Search**

### Intelligent Scientific Literature Explorer

**Discover, compare, and organize research across arXiv, Semantic Scholar & OpenAlex — powered by AI.**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)](https://react.dev)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.x-008CC1?logo=neo4j)](https://neo4j.com)
[![arXiv](https://img.shields.io/badge/arXiv-API-B31B1B)](https://arxiv.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[Features](#-features) · [Getting Started](#-getting-started) · [Architecture](#architecture) · [Contributing](CONTRIBUTING.md) · [Roadmap](#-roadmap)

</div>

---

## What is ReSearch?

A researcher-centric literature discovery and exploration tool that enables:
- Semantic search across scientific papers (arXiv, Semantic Scholar, OpenAlex)
- AI-powered summarization and paper comparison
- Trend and topic analysis with visual charts
- Workspace-based research organization with annotations
- Export to BibTeX and Markdown

Built for both:
- **Junior researchers** (learning & discovery)
- **Senior researchers** (analysis & workflow integration)

---

## The Problem

Academic paper discovery is broken:

| Problem | Impact |
|---------|--------|
| arXiv publishes **1,000+ papers daily** | Impossible to manually track |
| Research is siloed across databases | Related work is hidden |
| Reading time is limited | Hours wasted triaging irrelevant papers |
| No centralized workflow | Bookmarks, citations, and notes scattered |
| No cross-database search | Searching each source separately |

## The Solution

ReSearch aggregates **3 major research databases** into a single interface with AI-powered analysis:

| Capability | How ReSearch helps |
|------------|-------------------|
| **Multi-source search** | Search arXiv, Semantic Scholar & OpenAlex simultaneously |
| **AI summaries** | Gemini-powered plain-language summaries with key findings |
| **Paper comparison** | Side-by-side comparison matrix with AI analysis |
| **Trend analysis** | 10-year publication trend charts for any topic |
| **Workspaces** | Organize papers into projects with annotations and tags |
| **Export** | One-click BibTeX and Markdown export |
| **Graph recommendations** | Neo4j-powered citation and author-based suggestions |

---

## Who is this for?

| Persona | How ReSearch helps |
|---------|-------------------|
| **Graduate students** | Find papers for literature reviews, build reading lists, understand papers through AI summaries |
| **Researchers** | Discover related work via multi-source search, compare papers, track publication trends |
| **Professors** | Monitor new publications, organize curated paper collections in workspaces |
| **Independent learners** | Explore arXiv categories, get plain-language explanations of complex papers |
| **Lab teams** | Shared workspaces with annotations, exportable research packs |

---

## Features

### Multi-Source Discovery
- Search **arXiv** (2M+ papers), **Semantic Scholar** (200M+), and **OpenAlex** (250M+) simultaneously
- Filter by source, sort by relevance/citations/year
- Toggle databases on/off per search

### AI-Powered Analysis
- **Paper summaries** — One-click Gemini-powered summaries with key points and significance
- **Paper comparison** — Select 2-5 papers for side-by-side comparison with AI-generated analysis
- **"Why this paper matters"** snippets

### Trend Visualization
- 10-year publication trend charts for any search query
- Powered by OpenAlex metadata

### Workspaces & Annotations
- Create research projects (workspaces)
- Add papers from any source
- Annotate with notes and custom tags
- Export entire workspace to BibTeX or Markdown

### arXiv Deep Integration
- Search by keyword, author, abstract, or category
- Browse 28+ arXiv categories
- Latest papers feed (cs.AI, cs.LG, cs.CL, etc.)
- Full paper detail with metadata, PDF links, BibTeX export

### Reading List
- Save/unsave papers to personal library
- Persistent across sessions

### Graph Recommendations (Neo4j)
- Citation-based paper recommendations
- Author and venue-based discovery
- Popularity scoring

### Platform
- JWT authentication with secure registration
- Interest-based onboarding for personalized experience
- Dark academic theme designed for long reading sessions
- Responsive (desktop + mobile)
- Full OpenAPI/Swagger docs at `/docs`

---

## Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                   React 18 + Tailwind CSS                          │
│  Discover · arXiv · Latest · Library · Projects · Compare · Trends │
└──────────────────────────┬─────────────────────────────────────────┘
                           │ REST / JSON + JWT
                           ▼
┌────────────────────────────────────────────────────────────────────┐
│                     FastAPI (Python 3.11)                           │
│  ┌────────┐ ┌──────────┐ ┌────────┐ ┌──────┐ ┌────────────────┐  │
│  │  Auth  │ │ Discover │ │ arXiv  │ │Papers│ │ AI (Gemini)    │  │
│  │(JWT)   │ │(multi-   │ │(XML    │ │(Neo4j│ │ Summarize      │  │
│  │        │ │ source)  │ │ parse) │ │graph)│ │ Compare        │  │
│  └───┬────┘ └───┬──────┘ └───┬────┘ └──┬───┘ └────────┬───────┘  │
└──────┼──────────┼────────────┼─────────┼──────────────┼───────────┘
       ▼          ▼            ▼         ▼              ▼
  PostgreSQL  ┌─────────────────────┐  Neo4j       Gemini API
  (users,     │ Semantic Scholar    │  (graph)
   workspaces │ OpenAlex            │
   reading    │ arXiv               │
   list)      └─────────────────────┘
```

Full architecture docs: [report/Architecture.md](report/Architecture.md)

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+ (with Yarn)
- Neo4j 5.x (optional — graph features degrade gracefully)
- Gemini API key or Emergent LLM key (for AI features)

### 1. Clone

```bash
git clone https://github.com/your-org/research-paper-discovery.git
cd research-paper-discovery
```

### 2. Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # Edit with your credentials
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### 3. Frontend

```bash
cd frontend
yarn install
echo "REACT_APP_BACKEND_URL=http://localhost:8001" > .env
yarn start
```

### 4. Docker (alternative)

```bash
docker-compose up --build
```

Open `http://localhost:3000` — register, pick interests, and start discovering.

---

## API Reference

### Discovery (Multi-Source)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/discover/search` | Search across arXiv + S2 + OpenAlex |
| POST | `/api/discover/compare` | Compare 2-5 papers with AI analysis |
| GET | `/api/discover/trends` | 10-year publication trend data |

### Workspaces
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/api/discover/workspaces` | List / create workspaces |
| GET/PUT/DELETE | `/api/discover/workspaces/{id}` | Manage workspace |
| POST | `/api/discover/workspaces/{id}/papers` | Add paper to workspace |
| PUT | `/api/discover/workspaces/{id}/papers/{pid}/annotate` | Annotate paper |
| POST | `/api/discover/export` | Export papers (BibTeX/Markdown) |

### arXiv
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/arxiv/search` | Search arXiv papers |
| GET | `/api/arxiv/categories` | List categories |
| GET | `/api/arxiv/latest` | Latest by category |
| POST | `/api/arxiv/summarize` | AI paper summary |
| POST/DELETE | `/api/arxiv/save` | Save/unsave to library |

Full interactive docs: `http://localhost:8001/docs`

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | React 18, Tailwind CSS | Dark academic UI |
| Backend | FastAPI, Python 3.11 | REST API |
| SQL DB | PostgreSQL / SQLite | Users, workspaces, reading lists |
| Graph DB | Neo4j | Citation-based recommendations |
| Search | arXiv + Semantic Scholar + OpenAlex | Multi-source paper search |
| AI | Google Gemini (via Emergent) | Summarization, comparison |
| DevOps | Docker, Kubernetes | Containerized deployment |

---

## Project Structure

```
├── backend/
│   ├── routes/           # API endpoints (auth, arxiv, discover, papers, users)
│   ├── services/         # Business logic (arxiv, ai, semantic_scholar, openalex)
│   ├── models/           # SQLAlchemy models (User, Workspace, SavedPaper)
│   ├── schemas/          # Pydantic validation
│   ├── db/               # Database connections
│   └── server.py         # FastAPI entry point
├── frontend/src/
│   ├── pages/            # DiscoverPage, ComparePage, WorkspacesPage, ArxivSearchPage...
│   ├── components/       # Header, Card, Button, Input
│   ├── hooks/            # useAuth
│   └── lib/              # API client
├── k8s/                  # Kubernetes manifests
├── recommendation/       # Neo4j recommendation engine
├── CONTRIBUTING.md       # Contributor guidelines
├── CODE_OF_CONDUCT.md    # Community standards
├── docker-compose.yml    # Docker orchestration
└── report/Architecture.md # Full architecture docs
```

---

## Docker & Kubernetes

### Docker Compose

```bash
docker-compose up --build
# Frontend: http://localhost:3000
# Backend: http://localhost:8001/docs
```

### Kubernetes

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml     # Edit with your credentials first
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/ingress.yaml
```

See [k8s/README.md](k8s/README.md) for full deployment guide.

---

## Roadmap

### Phase 1 — Foundation (Done)
- [x] Multi-source search (arXiv + Semantic Scholar + OpenAlex)
- [x] AI paper summaries (Gemini)
- [x] Paper comparison with AI analysis
- [x] Trend visualization
- [x] Workspaces with annotations
- [x] Export (BibTeX / Markdown)
- [x] Dark academic theme
- [x] Docker + Kubernetes setup

### Phase 2 — UX & Collaboration
- [ ] Semantic/embedding-based search ranking
- [ ] User feedback (thumbs up/down) for relevance learning
- [ ] Shared workspaces & team annotations
- [ ] PDF viewer with inline highlighting

### Phase 3 — Research Analytics
- [ ] Topic clustering visualization
- [ ] Citation network graph explorer
- [ ] Author impact analysis
- [ ] Method/dataset extraction from papers

### Phase 4 — Integration & Ecosystem
- [ ] Zotero / Mendeley / EndNote import/export
- [ ] Notion / Obsidian plugin
- [ ] CLI tool for automation
- [ ] Plugin architecture for custom sources

---

## Feature Matrix

| Feature | Junior | Senior |
|---------|--------|--------|
| Multi-source search | Done | Done |
| AI summaries | Done | Done |
| Paper comparison | Done | Done |
| Export (BibTeX/MD) | Done | Done |
| Trend analytics | Done | Done |
| Workspaces + annotations | Done | Done |
| Graph recommendations | Done | Done |
| Semantic ranking | Planned | Planned |
| Shared workspaces | Planned | Planned |
| Plugin ecosystem | — | Planned |
| Citation graph explorer | — | Planned |

---

## Contributing

We welcome contributions of all sizes. See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup
- Coding standards
- Pull request process
- Good first issues

---

## License

MIT License — see [LICENSE](LICENSE).

## Acknowledgements

- [arXiv.org](https://arxiv.org) — Open API for 2M+ research papers
- [Semantic Scholar](https://www.semanticscholar.org/) — Academic graph with 200M+ papers
- [OpenAlex](https://openalex.org/) — Open catalog of 250M+ scholarly works
- [Google Gemini](https://deepmind.google/technologies/gemini/) — AI-powered analysis
- [Neo4j](https://neo4j.com/) — Graph database for recommendations

---

<div align="center">

**Built for researchers, by researchers.**

[Report Bug](../../issues) · [Request Feature](../../issues) · [Contribute](CONTRIBUTING.md)

</div>
