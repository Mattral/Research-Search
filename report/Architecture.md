# Re-Search System Architecture

This document describes the high-level architecture of the Re-Search application.

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Component Details](#component-details)
4. [Data Architecture](#data-architecture)
5. [Security Architecture](#security-architecture)
6. [Deployment Architecture](#deployment-architecture)

---

## System Overview

Re-Search follows a **three-tier architecture**:

| Tier | Components | Responsibility |
|------|------------|----------------|
| **Presentation** | React SPA | User interface, client-side routing |
| **Application** | FastAPI | Business logic, API endpoints |
| **Data** | SQLite + Neo4j | Data persistence, graph queries |

### Design Principles

1. **Separation of Concerns**: Each layer has distinct responsibilities
2. **Hybrid Database**: SQL for transactions, Graph for relationships
3. **Stateless API**: JWT tokens for authentication
4. **Component-Based UI**: Reusable React components

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              PRESENTATION TIER                           │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                        React Application                           │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐     │  │
│  │  │  Login  │ │Onboard- │ │ Search  │ │  Paper  │ │ Profile │     │  │
│  │  │  Page   │ │  ing    │ │  Page   │ │ Detail  │ │  Page   │     │  │
│  │  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘     │  │
│  │       │           │           │           │           │           │  │
│  │       └───────────┴───────────┼───────────┴───────────┘           │  │
│  │                               │                                    │  │
│  │                    ┌──────────┴──────────┐                        │  │
│  │                    │   Auth Context      │                        │  │
│  │                    │   API Client        │                        │  │
│  │                    └──────────┬──────────┘                        │  │
│  └───────────────────────────────┼───────────────────────────────────┘  │
└──────────────────────────────────┼──────────────────────────────────────┘
                                   │ HTTP/REST
                                   │ (JSON + JWT)
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                             APPLICATION TIER                             │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                       FastAPI Application                          │  │
│  │  ┌────────────────────────────────────────────────────────────┐   │  │
│  │  │                      Route Handlers                         │   │  │
│  │  │  ┌──────────┐    ┌──────────┐    ┌──────────┐              │   │  │
│  │  │  │   Auth   │    │  Papers  │    │  Users   │              │   │  │
│  │  │  │  Routes  │    │  Routes  │    │  Routes  │              │   │  │
│  │  │  └────┬─────┘    └────┬─────┘    └────┬─────┘              │   │  │
│  │  └───────┼───────────────┼───────────────┼────────────────────┘   │  │
│  │          │               │               │                         │  │
│  │  ┌───────┴───────────────┴───────────────┴────────────────────┐   │  │
│  │  │                       Services                              │   │  │
│  │  │  ┌──────────┐    ┌──────────┐    ┌──────────────────┐      │   │  │
│  │  │  │   Auth   │    │  Paper   │    │  Recommendation  │      │   │  │
│  │  │  │ Service  │    │ Service  │    │     Service      │      │   │  │
│  │  │  └────┬─────┘    └────┬─────┘    └────────┬─────────┘      │   │  │
│  │  └───────┼───────────────┼──────────────────┼─────────────────┘   │  │
│  └──────────┼───────────────┼──────────────────┼─────────────────────┘  │
└─────────────┼───────────────┼──────────────────┼────────────────────────┘
              │               │                  │
              ▼               ▼                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                               DATA TIER                                  │
│  ┌─────────────────────────┐    ┌─────────────────────────────────────┐ │
│  │      SQLite/PostgreSQL  │    │              Neo4j                  │ │
│  │  ┌───────────────────┐  │    │  ┌─────────────────────────────┐   │ │
│  │  │ Users             │  │    │  │         Papers              │   │ │
│  │  │ Interests         │  │    │  │    ┌───┐    ┌───┐          │   │ │
│  │  │ User_Interests    │  │    │  │    │ P │───>│ P │ (CITES)  │   │ │
│  │  │ User_Favorites    │  │    │  │    └───┘    └───┘          │   │ │
│  │  │ User_Recent_Views │  │    │  │      ▲                      │   │ │
│  │  └───────────────────┘  │    │  │      │                      │   │ │
│  │                         │    │  │    ┌───┐                    │   │ │
│  │  User transactions,     │    │  │    │ A │ (WROTE)           │   │ │
│  │  authentication,        │    │  │    └───┘                    │   │ │
│  │  favorites tracking     │    │  │                             │   │ │
│  └─────────────────────────┘    │  │  Graph relationships,       │   │ │
│                                 │  │  paper metadata,            │   │ │
│                                 │  │  recommendations            │   │ │
│                                 │  └─────────────────────────────┘   │ │
│                                 └─────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### Presentation Tier

#### React Application
- **Framework**: React 18 with functional components and hooks
- **Routing**: React Router v7 with protected routes
- **State Management**: React Context for global auth state
- **Styling**: Tailwind CSS with custom design system

#### Key Components

| Component | Purpose |
|-----------|---------|
| `AuthProvider` | Global authentication state |
| `Header` | Navigation with user interests |
| `LoginPage` | User authentication |
| `OnboardingPage` | Interest selection |
| `SearchPage` | Paper discovery |
| `PaperDetailPage` | Paper view with actions |
| `RecommendationsPage` | Personalized suggestions |
| `ProfilePage` | User settings |

### Application Tier

#### FastAPI Application
- **Framework**: FastAPI with async support
- **Validation**: Pydantic models for request/response
- **Documentation**: Auto-generated OpenAPI specs

#### Route Structure

```
/api
├── /auth
│   ├── POST /register      # Create account
│   ├── POST /login         # Get JWT token
│   ├── GET  /me            # Get profile
│   ├── PUT  /me            # Update profile
│   └── POST /change-password
│
├── /users
│   ├── GET  /interests     # List all interests
│   └── POST /interests     # Save user interests
│
└── /papers
    ├── GET  /search        # Search papers
    ├── GET  /browse        # Browse all
    ├── GET  /recommendations
    ├── GET  /{id}          # Paper details
    ├── POST /{id}/view     # Track view
    ├── POST /{id}/like     # Like paper
    ├── DELETE /{id}/like   # Unlike paper
    ├── GET  /me/favorites
    └── GET  /me/recent-views
```

### Data Tier

#### Why Hybrid Database?

| Use Case | Best Fit | Reason |
|----------|----------|--------|
| User authentication | SQL | ACID transactions, simple queries |
| Session management | SQL | Relational data, foreign keys |
| Paper relationships | Graph | Natural representation of citations |
| Recommendations | Graph | Efficient traversal queries |
| User favorites | Both | SQL for storage, Graph for recs |

---

## Data Architecture

### Data Flow Patterns

#### Read Path (Search)
```
User Request
    │
    ▼
┌─────────────┐
│ API Gateway │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐
│  FastAPI    │────>│   Neo4j     │
│  Router     │     │   Query     │
└──────┬──────┘     └──────┬──────┘
       │                   │
       │      ┌────────────┘
       │      │
       ▼      ▼
┌─────────────────┐
│ Merge & Format  │
└────────┬────────┘
         │
         ▼
    JSON Response
```

#### Write Path (Like Paper)
```
Like Request
    │
    ▼
┌─────────────┐
│  Validate   │
│    JWT      │
└──────┬──────┘
       │
       ├──────────────────┐
       ▼                  ▼
┌─────────────┐    ┌─────────────┐
│   SQLite    │    │   Neo4j     │
│   INSERT    │    │   MERGE     │
│  favorite   │    │  LIKED rel  │
└──────┬──────┘    └──────┬──────┘
       │                  │
       └────────┬─────────┘
                │
                ▼
         Success Response
```

### Caching Strategy

| Data Type | Cache Location | TTL |
|-----------|---------------|-----|
| JWT Token | localStorage | 24h |
| User Profile | React State | Session |
| Search Results | None | Real-time |
| Interests | Server memory | App lifetime |

---

## Security Architecture

### Authentication Flow

```
┌──────────┐                    ┌──────────┐
│  Client  │                    │  Server  │
└────┬─────┘                    └────┬─────┘
     │                               │
     │  1. Login (email, password)   │
     │──────────────────────────────>│
     │                               │
     │                    ┌──────────┴──────────┐
     │                    │ 2. Verify password  │
     │                    │ 3. Generate JWT     │
     │                    └──────────┬──────────┘
     │                               │
     │  4. Return JWT token          │
     │<──────────────────────────────│
     │                               │
     │  5. Store in localStorage     │
     │                               │
     │  6. API Request + JWT         │
     │──────────────────────────────>│
     │                               │
     │                    ┌──────────┴──────────┐
     │                    │ 7. Validate JWT     │
     │                    │ 8. Extract user_id  │
     │                    │ 9. Authorize action │
     │                    └──────────┬──────────┘
     │                               │
     │  10. Return data              │
     │<──────────────────────────────│
```

### Security Measures

| Threat | Mitigation |
|--------|------------|
| Password theft | bcrypt hashing (cost factor 12) |
| Token theft | Short expiry (24h), HTTPS |
| SQL Injection | SQLAlchemy ORM, parameterized queries |
| Cypher Injection | Parameterized Neo4j queries |
| XSS | React auto-escaping |
| CSRF | JWT in Authorization header |

### JWT Token Structure

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "1",        // User ID
    "exp": 1706000000  // Expiration
  },
  "signature": "..."
}
```

---

## Deployment Architecture

### Development Environment

```
┌────────────────────────────────────────────────┐
│                  Developer Machine             │
│  ┌──────────────┐    ┌──────────────┐         │
│  │   Frontend   │    │   Backend    │         │
│  │  localhost   │───>│  localhost   │         │
│  │    :3000     │    │    :8001     │         │
│  └──────────────┘    └──────┬───────┘         │
│                             │                  │
│         ┌───────────────────┼───────────────┐ │
│         │                   │               │ │
│         ▼                   ▼               │ │
│  ┌──────────────┐    ┌──────────────┐       │ │
│  │    SQLite    │    │  Neo4j Cloud │       │ │
│  │  (local file)│    │   (remote)   │       │ │
│  └──────────────┘    └──────────────┘       │ │
└────────────────────────────────────────────────┘
```

### Production Environment (Recommended)

```
┌─────────────────────────────────────────────────────────────────┐
│                         Load Balancer                            │
│                        (nginx/CloudFlare)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
              ▼                             ▼
┌─────────────────────────┐    ┌─────────────────────────┐
│     Frontend Server     │    │     Backend Server      │
│   (Static files/CDN)    │    │      (FastAPI)          │
│   ┌─────────────────┐   │    │   ┌─────────────────┐   │
│   │  React Build    │   │    │   │   Gunicorn      │   │
│   │  (index.html,   │   │    │   │   + Uvicorn     │   │
│   │   bundle.js)    │   │    │   │   workers       │   │
│   └─────────────────┘   │    │   └────────┬────────┘   │
└─────────────────────────┘    └────────────┼────────────┘
                                            │
                         ┌──────────────────┼──────────────────┐
                         │                  │                  │
                         ▼                  ▼                  ▼
              ┌──────────────────┐ ┌──────────────┐ ┌──────────────┐
              │   PostgreSQL     │ │  Neo4j Aura  │ │    Redis     │
              │   (Primary DB)   │ │   (Graph)    │ │  (Sessions)  │
              └──────────────────┘ └──────────────┘ └──────────────┘
```

### Container Deployment (Docker)

```yaml
# docker-compose.yml (conceptual)
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "8001:8001"
    environment:
      - DATABASE_URL
      - NEO4J_URI
      - JWT_SECRET
    depends_on:
      - postgres

  postgres:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

## Scalability Considerations

### Horizontal Scaling

| Component | Strategy |
|-----------|----------|
| Frontend | CDN distribution, static hosting |
| Backend | Multiple Gunicorn workers, load balancer |
| PostgreSQL | Read replicas, connection pooling |
| Neo4j | Aura Enterprise with clustering |

### Performance Optimization

1. **Database Indexing**
   ```sql
   -- PostgreSQL
   CREATE INDEX idx_users_email ON users(email);
   CREATE INDEX idx_favorites_user ON user_favorites(user_id);
   ```
   
   ```cypher
   -- Neo4j
   CREATE INDEX FOR (p:Paper) ON (p.id);
   CREATE INDEX FOR (a:Author) ON (a.name);
   ```

2. **Query Optimization**
   - Limit result sets (max 100 papers per query)
   - Use projections in Neo4j queries
   - Avoid N+1 queries with batch loading

3. **Caching Layer** (Future)
   - Redis for session management
   - CDN for static assets
   - Query result caching

---

## Monitoring & Logging

### Recommended Stack

| Tool | Purpose |
|------|---------|
| Prometheus | Metrics collection |
| Grafana | Visualization |
| ELK Stack | Log aggregation |
| Sentry | Error tracking |

### Key Metrics

- API response times
- Error rates by endpoint
- Database query performance
- Neo4j query execution times
- JWT validation failures
- User registration/login rates
