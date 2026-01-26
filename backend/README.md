# Re-Search Backend

A FastAPI-powered backend for the Research Paper Discovery & Recommendation System.

## Overview

This backend provides REST APIs for:
- User authentication (JWT-based)
- Paper search and discovery (Neo4j graph database)
- Personalized recommendations using graph traversal
- User profile management

## Tech Stack

- **Framework**: FastAPI 0.104.1
- **Database**: SQLite (user data) + Neo4j (paper graph)
- **Authentication**: JWT with python-jose
- **Password Hashing**: bcrypt via passlib

## Project Structure

```
backend/
├── db/
│   ├── neo4j.py          # Neo4j connection manager
│   └── postgres.py       # SQLite/PostgreSQL connection
├── models/
│   └── user_models.py    # SQLAlchemy ORM models
├── routes/
│   ├── auth_routes.py    # Authentication endpoints
│   ├── paper_routes.py   # Paper & recommendation endpoints
│   └── user_routes.py    # User management endpoints
├── schemas/
│   ├── paper_schemas.py  # Pydantic models for papers
│   └── user_schemas.py   # Pydantic models for users
├── services/
│   ├── auth_service.py   # JWT & password utilities
│   ├── paper_service.py  # Neo4j paper queries
│   └── recommendation_service.py  # Recommendation engine
├── server.py             # Main FastAPI application
├── seed_data.py          # Sample data seeder
├── requirements.txt      # Python dependencies
└── .env                  # Environment variables
```

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login and get JWT token |
| GET | `/api/auth/me` | Get current user profile |
| PUT | `/api/auth/me` | Update user profile |
| POST | `/api/auth/change-password` | Change password |

### Papers
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/papers/search` | Search papers by title/author/year |
| GET | `/api/papers/browse` | Browse all papers |
| GET | `/api/papers/{id}` | Get paper details |
| POST | `/api/papers/{id}/view` | Track paper view |
| POST | `/api/papers/{id}/like` | Like/save a paper |
| DELETE | `/api/papers/{id}/like` | Unlike a paper |
| GET | `/api/papers/recommendations` | Get personalized recommendations |
| GET | `/api/papers/me/favorites` | Get user's liked papers |
| GET | `/api/papers/me/recent-views` | Get recently viewed papers |

### Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users/interests` | Get all available interests |
| POST | `/api/users/interests` | Save user's selected interests |

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables (see .env.example)
cp .env.example .env

# Run the server
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEO4J_URI` | Neo4j connection URI | - |
| `NEO4J_USER` | Neo4j username | neo4j |
| `NEO4J_PASSWORD` | Neo4j password | - |
| `DATABASE_URL` | SQLite/PostgreSQL URL | sqlite:///./research.db |
| `JWT_SECRET` | Secret key for JWT | - |
| `JWT_ALGORITHM` | JWT algorithm | HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry | 1440 |

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

## Recommendation Algorithm

The recommendation engine uses graph traversal with multiple strategies:
1. **Citation-based**: Papers cited by papers you liked
2. **Author-based**: Papers by authors you've read
3. **Venue-based**: Papers from venues you follow
4. **Popularity**: Highly cited papers in your field

Each candidate is scored using weighted factors and returned with explanations.

## License

MIT
