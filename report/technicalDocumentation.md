# Re-Search Technical Documentation

This document provides detailed technical documentation for the Re-Search application.

## Table of Contents
1. [System Overview](#system-overview)
2. [Backend Architecture](#backend-architecture)
3. [Frontend Architecture](#frontend-architecture)
4. [Database Schema](#database-schema)
5. [API Reference](#api-reference)
6. [Authentication Flow](#authentication-flow)
7. [Recommendation Engine](#recommendation-engine)
8. [Data Flow](#data-flow)

---

## System Overview

Re-Search is a full-stack research paper discovery platform that combines:
- **Relational Database** (SQLite/PostgreSQL) for user management
- **Graph Database** (Neo4j) for paper relationships and recommendations
- **REST API** (FastAPI) for backend services
- **Single Page Application** (React) for the frontend

### Key Features
- User authentication with JWT tokens
- Interest-based onboarding
- Paper search across multiple dimensions
- Graph-based recommendation engine
- User activity tracking

---

## Backend Architecture

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | FastAPI | REST API & async support |
| ORM | SQLAlchemy | Database abstraction |
| Validation | Pydantic | Request/response validation |
| Auth | python-jose | JWT token handling |
| Password | passlib + bcrypt | Secure password hashing |
| Neo4j Driver | neo4j-python | Graph database client |

### Directory Structure

```
backend/
├── db/                    # Database connections
│   ├── neo4j.py          # Neo4j connection singleton
│   └── postgres.py       # SQLAlchemy setup
├── models/               # ORM models
│   └── user_models.py    # User, Interest, Favorite models
├── routes/               # API route handlers
│   ├── auth_routes.py    # /api/auth/*
│   ├── paper_routes.py   # /api/papers/*
│   └── user_routes.py    # /api/users/*
├── schemas/              # Pydantic schemas
│   ├── paper_schemas.py  # Paper DTOs
│   └── user_schemas.py   # User DTOs
├── services/             # Business logic
│   ├── auth_service.py   # JWT & password utilities
│   ├── paper_service.py  # Neo4j queries
│   └── recommendation_service.py
└── server.py             # FastAPI app entry point
```

### Key Classes and Functions

#### Neo4jConnection (db/neo4j.py)
```python
class Neo4jConnection:
    """Singleton connection manager for Neo4j"""
    
    @classmethod
    def get_driver(cls):
        """Returns Neo4j driver, creates if not exists"""
        # Tries cloud connection first, falls back to local
        
    @classmethod
    def close(cls):
        """Closes the Neo4j connection"""
```

#### Authentication Service (services/auth_service.py)
```python
def create_access_token(data: dict) -> str:
    """Creates JWT token with expiration"""
    
def decode_token(token: str) -> TokenData:
    """Decodes and validates JWT token"""
    
async def get_current_user(credentials, db) -> User:
    """Dependency that extracts user from JWT"""
```

---

## Frontend Architecture

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | React 18 | UI library |
| Routing | React Router 7 | Client-side routing |
| Styling | Tailwind CSS | Utility-first CSS |
| HTTP | Axios | API requests |
| State | React Context | Global state (auth) |
| Icons | Lucide React | Icon library |
| Toasts | Sonner | Notifications |

### Component Hierarchy

```
App
├── AuthProvider (Context)
│   ├── PublicRoute
│   │   ├── LoginPage
│   │   └── RegisterPage
│   └── ProtectedRoute
│       ├── OnboardingGuard
│       │   ├── SearchPage
│       │   ├── PaperDetailPage
│       │   ├── RecommendationsPage
│       │   └── ProfilePage
│       └── OnboardingPage
└── Toaster
```

### State Management

#### Auth Context (hooks/useAuth.js)
```javascript
const AuthContext = {
  user: User | null,
  token: string | null,
  loading: boolean,
  login: (email, password) => Promise,
  register: (email, username, password, fullName) => Promise,
  logout: () => void,
  updateUser: (userData) => void,
  isAuthenticated: boolean
}
```

### API Client (lib/api.js)
```javascript
// Axios instance with interceptors
const api = axios.create({
  baseURL: process.env.REACT_APP_BACKEND_URL
});

// Auto-attach JWT token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Handle 401 errors
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // Redirect to login
    }
  }
);
```

---

## Database Schema

### SQLite/PostgreSQL Schema

#### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    has_completed_onboarding BOOLEAN DEFAULT FALSE
);
```

#### Interests Table
```sql
CREATE TABLE interests (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    icon VARCHAR(50),
    image_url VARCHAR(500)
);
```

#### User Interests (Many-to-Many)
```sql
CREATE TABLE user_interests (
    user_id INTEGER REFERENCES users(id),
    interest_id INTEGER REFERENCES interests(id),
    PRIMARY KEY (user_id, interest_id)
);
```

#### User Favorites
```sql
CREATE TABLE user_favorites (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    paper_id VARCHAR(100) NOT NULL,
    paper_title VARCHAR(500),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### User Recent Views
```sql
CREATE TABLE user_recent_views (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    paper_id VARCHAR(100) NOT NULL,
    paper_title VARCHAR(500),
    viewed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Neo4j Graph Schema

#### Node Types
```cypher
(:Paper {id, title, abstract, year, url})
(:Author {name})
(:Venue {name})
(:User {id})
```

#### Relationships
```cypher
(:Author)-[:WROTE]->(:Paper)
(:Paper)-[:PUBLISHED_IN]->(:Venue)
(:Paper)-[:CITES]->(:Paper)
(:User)-[:LIKED]->(:Paper)
(:User)-[:VIEWED]->(:Paper)
```

---

## API Reference

### Authentication Endpoints

#### POST /api/auth/register
**Request:**
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "secret123",
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "full_name": "John Doe",
    "has_completed_onboarding": false,
    "interests": [],
    "created_at": "2024-01-26T12:00:00"
  }
}
```

#### POST /api/auth/login
**Request:**
```json
{
  "email": "user@example.com",
  "password": "secret123"
}
```

### Paper Endpoints

#### GET /api/papers/search
**Query Parameters:**
- `title` (optional): Search by title
- `author` (optional): Search by author name
- `year` (optional): Filter by year
- `limit` (default: 20): Max results

**Response:**
```json
[
  {
    "paper_id": "paper_001",
    "title": "Deep Learning for NLP",
    "abstract": "This paper...",
    "year": 2023,
    "authors": ["John Smith", "Jane Doe"],
    "venue": "NeurIPS 2023",
    "citation_count": 42,
    "url": "https://...",
    "is_liked": false
  }
]
```

#### GET /api/papers/recommendations
**Response:**
```json
[
  {
    "paper_id": "paper_002",
    "title": "Attention Mechanisms",
    "score": 0.75,
    "reason": "Cited by a paper you liked; Same author",
    "authors": ["Alice Johnson"],
    "year": 2023,
    "venue": "ICML 2023"
  }
]
```

---

## Authentication Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  Client  │     │  Backend │     │ Database │
└────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │
     │ POST /login    │                │
     │───────────────>│                │
     │                │ Query user     │
     │                │───────────────>│
     │                │                │
     │                │ User data      │
     │                │<───────────────│
     │                │                │
     │                │ Verify password│
     │                │ Generate JWT   │
     │                │                │
     │ JWT Token      │                │
     │<───────────────│                │
     │                │                │
     │ GET /papers    │                │
     │ (with JWT)     │                │
     │───────────────>│                │
     │                │ Decode JWT     │
     │                │ Validate user  │
     │                │                │
     │ Papers data    │                │
     │<───────────────│                │
```

### JWT Token Structure
```json
{
  "sub": "1",           // User ID (string)
  "exp": 1706000000     // Expiration timestamp
}
```

---

## Recommendation Engine

### Algorithm Overview

The recommendation engine uses a multi-strategy approach:

```
┌─────────────────────────────────────────────────────┐
│                 User Activity                        │
│  (Liked Papers, Viewed Papers, Selected Interests)  │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│              Candidate Generation                    │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐         │
│  │ Citation  │ │  Author   │ │  Venue    │         │
│  │   Based   │ │   Based   │ │   Based   │         │
│  └─────┬─────┘ └─────┬─────┘ └─────┬─────┘         │
│        │             │             │                │
│        └─────────────┼─────────────┘                │
│                      ▼                              │
│              Merge Candidates                       │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│                   Scoring                           │
│  score = 0.4 * is_cited                            │
│        + 0.25 * same_author                        │
│        + 0.25 * same_venue                         │
│        + 0.1 * popularity                          │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│              Ranked Results                         │
│  (Sorted by score with explanations)               │
└─────────────────────────────────────────────────────┘
```

### Neo4j Queries

#### Citation-Based Recommendations
```cypher
MATCH (u:User {id: $userId})-[:LIKED|VIEWED]->(liked:Paper)
MATCH (liked)-[:CITES]->(rec:Paper)
WHERE NOT (u)-[:LIKED|VIEWED]->(rec)
RETURN rec, COUNT(DISTINCT liked) as relevance
ORDER BY relevance DESC
LIMIT 15
```

#### Author-Based Recommendations
```cypher
MATCH (u:User {id: $userId})-[:LIKED|VIEWED]->(liked:Paper)
MATCH (a:Author)-[:WROTE]->(liked)
MATCH (a)-[:WROTE]->(rec:Paper)
WHERE NOT (u)-[:LIKED|VIEWED]->(rec) AND liked <> rec
RETURN rec, collect(DISTINCT a.name) as commonAuthors
```

### Scoring Function
```python
def calculate_score(paper):
    score = 0.0
    reasons = []
    
    if paper.get("is_cited"):
        score += 0.4
        reasons.append("Cited by a paper you liked")
    
    if paper.get("same_author"):
        score += 0.25
        reasons.append("Same author")
    
    if paper.get("same_venue"):
        score += 0.25
        reasons.append("Same venue")
    
    score += 0.1 * paper.get("popularity", 0)
    
    return round(score, 2), reasons
```

---

## Data Flow

### Search Flow
```
User Input → SearchPage → API Client → Backend Router 
    → Paper Service → Neo4j Query → Results 
    → Response → UI Update
```

### Like Paper Flow
```
Click Like → paperAPI.likePaper() 
    → POST /api/papers/{id}/like
    → Save to SQLite (user_favorites)
    → Create Neo4j relationship (:User)-[:LIKED]->(:Paper)
    → Return success
    → Update UI state
```

### Recommendation Flow
```
Request Recommendations 
    → GET /api/papers/recommendations
    → Get user history from SQLite
    → Execute Neo4j graph queries (citation, author, venue, popularity)
    → Merge candidates
    → Calculate scores
    → Sort by score
    → Return top N with reasons
```

---

## Error Handling

### Backend Error Responses
```python
# 400 Bad Request
HTTPException(status_code=400, detail="Email already registered")

# 401 Unauthorized
HTTPException(status_code=401, detail="Could not validate credentials")

# 404 Not Found
HTTPException(status_code=404, detail="Paper not found")
```

### Frontend Error Handling
```javascript
try {
  const response = await paperAPI.search(params);
  setPapers(response.data);
} catch (error) {
  toast.error(error.response?.data?.detail || 'Search failed');
}
```

---

## Performance Considerations

1. **Neo4j Indexing**: Ensure indexes on frequently queried properties
   ```cypher
   CREATE INDEX paper_id_idx FOR (p:Paper) ON (p.id)
   CREATE INDEX author_name_idx FOR (a:Author) ON (a.name)
   ```

2. **Query Limits**: All queries have LIMIT clauses to prevent large result sets

3. **Connection Pooling**: Neo4j driver maintains connection pool automatically

4. **JWT Caching**: Tokens are stored in localStorage to avoid re-authentication

5. **Lazy Loading**: Recommendations are fetched on-demand, not on page load
