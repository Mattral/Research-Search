# ReSearch System Architecture

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Component Details](#component-details)
4. [Data Architecture](#data-architecture)
5. [arXiv Integration](#arxiv-integration)
6. [AI Service](#ai-service)
7. [Security Architecture](#security-architecture)
8. [Deployment Architecture](#deployment-architecture)

---

## System Overview

ReSearch follows a **four-tier architecture** with two external service integrations:

| Tier | Components | Responsibility |
|------|------------|----------------|
| **Presentation** | React SPA | User interface, client-side routing, dark academic theme |
| **Application** | FastAPI | Business logic, API endpoints, authentication |
| **Data** | PostgreSQL/SQLite + Neo4j | User data + graph-based paper relationships |
| **External** | arXiv API + Gemini AI | Live paper search + AI summarization |

### Design Principles

1. **Separation of Concerns** — Each layer has distinct responsibilities
2. **Hybrid Database** — SQL for transactions, Graph for relationships
3. **Graceful Degradation** — Neo4j and AI features are optional; core search works without them
4. **Stateless API** — JWT tokens for authentication, no server-side sessions
5. **External API Isolation** — arXiv and Gemini calls are in dedicated service modules

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          PRESENTATION TIER                              │
│                                                                         │
│   React 18 + Tailwind CSS (Dark Academic Theme)                        │
│                                                                         │
│   ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐         │
│   │ ArxivSearch│ │ArxivPaper  │ │LatestPapers│ │ReadingList │         │
│   │   Page     │ │   Page     │ │   Page     │ │   Page     │         │
│   └─────┬──────┘ └─────┬──────┘ └─────┬──────┘ └─────┬──────┘         │
│         │               │               │               │               │
│   ┌─────┴──────┐ ┌─────┴──────┐ ┌─────┴──────┐ ┌─────┴──────┐         │
│   │ SearchPage │ │PaperDetail │ │  Recommend  │ │  Profile   │         │
│   │  (Graph)   │ │  (Graph)   │ │   Page      │ │   Page     │         │
│   └─────┬──────┘ └─────┬──────┘ └─────┬──────┘ └─────┬──────┘         │
│         └───────────────┴───────────────┴───────────────┘               │
│                              │                                          │
│                    ┌─────────┴─────────┐                                │
│                    │ Auth Context       │                                │
│                    │ API Client (axios) │                                │
│                    └─────────┬─────────┘                                │
└──────────────────────────────┼──────────────────────────────────────────┘
                               │ REST / JSON + JWT
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          APPLICATION TIER                                │
│                                                                         │
│   FastAPI (Python 3.11)                                                │
│                                                                         │
│   ┌──────────────────────────────────────────────────────────────┐      │
│   │                        Route Handlers                        │      │
│   │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │      │
│   │  │  Auth    │ │  arXiv   │ │  Papers  │ │  Users   │       │      │
│   │  │ Routes   │ │  Routes  │ │  Routes  │ │  Routes  │       │      │
│   │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘       │      │
│   └───────┼─────────────┼────────────┼────────────┼─────────────┘      │
│           │             │            │            │                      │
│   ┌───────┴─────────────┴────────────┴────────────┴─────────────┐      │
│   │                        Services                              │      │
│   │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │      │
│   │  │  Auth    │ │  arXiv   │ │  Paper   │ │     AI       │   │      │
│   │  │ Service  │ │ Service  │ │ Service  │ │   Service    │   │      │
│   │  │ (JWT)    │ │ (HTTP+   │ │ (Neo4j)  │ │  (Gemini)   │   │      │
│   │  │          │ │  XML)    │ │          │ │              │   │      │
│   │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └──────┬───────┘   │      │
│   └───────┼─────────────┼────────────┼──────────────┼───────────┘      │
└───────────┼─────────────┼────────────┼──────────────┼──────────────────┘
            │             │            │              │
            ▼             ▼            ▼              ▼
┌───────────────┐ ┌──────────────┐ ┌───────────┐ ┌───────────┐
│  PostgreSQL   │ │  arXiv.org   │ │   Neo4j   │ │  Google   │
│   / SQLite    │ │  Public API  │ │  (Graph)  │ │  Gemini   │
│               │ │              │ │           │ │           │
│  Users        │ │  2M+ papers  │ │  Papers   │ │  AI text  │
│  Favorites    │ │  Atom XML    │ │  Authors  │ │  summary  │
│  Reading List │ │  Categories  │ │  Venues   │ │           │
│  Interests    │ │              │ │  Cites    │ │           │
└───────────────┘ └──────────────┘ └───────────┘ └───────────┘
```

---

## Component Details

### Presentation Tier

| Component | Purpose | Tech |
|-----------|---------|------|
| `ArxivSearchPage` | Search arXiv with filters, pagination | React, axios |
| `ArxivPaperPage` | Paper detail + AI summary | React, Gemini |
| `LatestPapersPage` | Category-based latest feed | React |
| `ReadingListPage` | Saved papers management | React |
| `SearchPage` | Graph-based paper search (Neo4j) | React |
| `RecommendationsPage` | Personalized recommendations | React |
| `Header` | Navigation with 6 main routes | React Router |
| `AuthProvider` | JWT-based auth state management | React Context |

### Application Tier

| Route Group | Prefix | Endpoints |
|-------------|--------|-----------|
| Auth | `/api/auth` | register, login, me, change-password |
| arXiv | `/api/arxiv` | search, categories, latest, paper, summarize, save, reading-list |
| Papers | `/api/papers` | search, browse, recommendations, like, view |
| Users | `/api/users` | interests |

### Service Layer

| Service | Responsibility | External Dependency |
|---------|---------------|-------------------|
| `auth_service` | JWT creation/validation, password hashing | None |
| `arxiv_service` | HTTP calls to arXiv API, Atom XML parsing | arXiv.org |
| `paper_service` | Cypher queries for paper CRUD | Neo4j |
| `ai_service` | LLM-powered summarization | Gemini API |
| `recommendation_service` | Multi-signal scoring algorithm | Neo4j |

---

## arXiv Integration

### Data Flow

```
User Query
    │
    ▼
┌─────────────────┐
│ /api/arxiv/search│
│ (FastAPI route)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────────────────────┐
│ arxiv_service   │────▶│ https://export.arxiv.org/api/   │
│ build query     │     │ query?search_query=...          │
│ URL encode      │     │ &start=0&max_results=20         │
└────────┬────────┘     │ &sortBy=relevance               │
         │              └──────────────┬──────────────────┘
         │                             │
         │              ┌──────────────┴──────────────────┐
         │              │ Atom XML Response               │
         │              │ <feed>                          │
         │              │   <opensearch:totalResults>     │
         │              │   <entry> (per paper)           │
         │              │     <title>, <summary>,         │
         │              │     <author>, <category>,       │
         │              │     <link> (pdf, abs, doi)      │
         │              │   </entry>                      │
         │              │ </feed>                         │
         │              └──────────────┬──────────────────┘
         │                             │
         ▼                             ▼
┌─────────────────┐     ┌──────────────────────────┐
│ _parse_feed()   │◀────│ XML → Dict conversion    │
│ _parse_entry()  │     │ Namespace-aware parsing   │
└────────┬────────┘     └──────────────────────────┘
         │
         ▼
┌─────────────────┐
│ Mark saved      │  (check SavedArxivPaper table)
│ Return JSON     │
└─────────────────┘
```

### arXiv Search Fields

| Prefix | Searches in |
|--------|------------|
| `all` | Title + Author + Abstract + Comment + Journal Ref |
| `ti` | Title only |
| `au` | Author name |
| `abs` | Abstract only |
| `cat` | Subject category |

### Rate Limiting

Per arXiv API terms: minimum 3-second delay between consecutive calls. The service uses `httpx` async client with 30s timeout. Results are cached on the client side per session.

---

## AI Service

### Summarization Flow

```
Paper abstract
    │
    ▼
┌──────────────┐
│ Structured   │  "SUMMARY: ... KEY_POINTS: - ... SIGNIFICANCE: ..."
│ prompt       │
└──────┬───────┘
       │
       ▼
┌──────────────┐     ┌─────────────────┐
│ Gemini 2.0   │────▶│ google-genai    │
│ Flash        │     │ (via Emergent   │
│              │     │  LLM key)       │
└──────┬───────┘     └─────────────────┘
       │
       ▼
┌──────────────┐
│ Parse        │  Extract SUMMARY, KEY_POINTS, SIGNIFICANCE sections
│ response     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Return JSON  │  { summary, key_points[], significance }
└──────────────┘
```

---

## Security Architecture

### Authentication Flow

```
Client                              Server
  │                                    │
  │  POST /api/auth/login             │
  │  { email, password }              │
  │───────────────────────────────────▶│
  │                                    │  bcrypt.verify(password, hash)
  │                                    │  jwt.encode({ sub: user_id })
  │  200 { access_token, user }       │
  │◀───────────────────────────────────│
  │                                    │
  │  GET /api/arxiv/search            │
  │  Authorization: Bearer <token>    │
  │───────────────────────────────────▶│
  │                                    │  jwt.decode(token)
  │                                    │  db.query(User, id=sub)
  │  200 { papers }                   │
  │◀───────────────────────────────────│
```

### Security Measures

| Threat | Mitigation |
|--------|------------|
| Password theft | bcrypt hashing (cost factor 12) |
| Token theft | Short expiry (24h), HTTPS |
| SQL Injection | SQLAlchemy ORM, parameterized queries |
| Cypher Injection | Parameterized Neo4j queries |
| XSS | React auto-escaping |
| CSRF | JWT in Authorization header (not cookies) |

---

## Deployment Architecture

### Docker Compose (Development / Small Teams)

```
┌────────────────────────────────────────────────┐
│  docker-compose up                             │
│                                                │
│  ┌──────────────┐    ┌──────────────┐         │
│  │   Frontend   │───▶│   Backend    │         │
│  │  nginx:3000  │    │  uvicorn     │         │
│  │  (React SPA) │    │  :8001       │         │
│  └──────────────┘    └──────┬───────┘         │
│                             │                  │
│                    ┌────────┴────────┐         │
│                    ▼                 ▼         │
│            ┌──────────────┐  ┌────────────┐   │
│            │  PostgreSQL  │  │ Neo4j Aura │   │
│            │  (container) │  │ (external) │   │
│            └──────────────┘  └────────────┘   │
└────────────────────────────────────────────────┘
```

### Kubernetes (Production)

```
┌─────────────────────────────────────────────────────────────────┐
│                     Kubernetes Cluster                           │
│                                                                 │
│  ┌──────────────────────────────────────────────────────┐      │
│  │                    Ingress                            │      │
│  │         /api/* → backend:8001                        │      │
│  │         /*     → frontend:3000                       │      │
│  └──────────────────────┬───────────────────────────────┘      │
│                         │                                       │
│          ┌──────────────┴──────────────┐                       │
│          │                             │                        │
│  ┌───────┴──────────┐     ┌───────────┴────────┐              │
│  │ Frontend Deploy  │     │  Backend Deploy    │              │
│  │ replicas: 2      │     │  replicas: 2       │              │
│  │ nginx + React    │     │  FastAPI + uvicorn │              │
│  │ CPU: 100-200m    │     │  CPU: 250-500m     │              │
│  │ Mem: 128-256Mi   │     │  Mem: 256-512Mi    │              │
│  └──────────────────┘     └────────┬───────────┘              │
│                                    │                           │
│                    ┌───────────────┴──────────────┐            │
│                    │                              │             │
│           ┌────────┴────────┐          ┌──────────┴─────┐      │
│           │ PostgreSQL      │          │ External:      │      │
│           │ StatefulSet     │          │ Neo4j Aura     │      │
│           │ PVC: 5Gi        │          │ Gemini API     │      │
│           └─────────────────┘          └────────────────┘      │
└─────────────────────────────────────────────────────────────────┘
```

---

## Scalability Considerations

| Component | Horizontal Scaling | Bottleneck |
|-----------|-------------------|------------|
| Frontend | CDN + replicas | Static, scales easily |
| Backend | Multiple replicas | arXiv API rate limit (3s between calls) |
| PostgreSQL | Read replicas | Write throughput |
| Neo4j | Aura Enterprise clustering | Query complexity |
| Gemini AI | Per-key rate limits | API quota |

### Performance Targets

| Metric | Target |
|--------|--------|
| arXiv search response | < 3s (dependent on arXiv API) |
| Graph search response | < 500ms |
| AI summary generation | < 5s |
| Page load (frontend) | < 2s |
| API p99 latency | < 1s (excluding arXiv/AI calls) |
