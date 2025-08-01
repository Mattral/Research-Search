# Re-Search - Research Paper Discovery & Recommendation System

## Product Overview
A full-stack research paper discovery platform combining relational (SQLite/PostgreSQL) and graph (Neo4j) databases for intelligent paper recommendations.

## Architecture
- **Frontend**: React 18 with Tailwind CSS, lucide-react icons, sonner toasts
- **Backend**: FastAPI with Python 3.11
- **Databases**: 
  - SQLite (user data, auth, favorites, history)
  - Neo4j (paper relationships, citations, authors, venues)
- **Authentication**: JWT-based with bcrypt password hashing

## User Personas
1. **Researchers**: Find papers related to their work, track citations
2. **Students**: Discover papers for coursework and thesis
3. **Academics**: Track papers in their field, find collaborators

## Core Requirements (Static)
- User authentication (register/login)
- Pinterest-style interest onboarding
- Paper search by title, author, year
- Paper detail view with abstract, citations
- Like/save papers to favorites
- Graph-based recommendations
- User profile with history

## What's Been Implemented (Jan 26, 2026)

### Backend
- [x] User registration/login with JWT auth
- [x] Interest selection API
- [x] Paper search (Neo4j graph queries)
- [x] Paper browse/discovery
- [x] Paper detail with citations
- [x] Like/unlike paper
- [x] Track paper views
- [x] Personalized recommendations
- [x] User profile APIs
- [x] Change password
- [x] Health check endpoint

### Frontend
- [x] Login page with validation
- [x] Registration page
- [x] Pinterest-style onboarding with 16 interest categories
- [x] Search page with filters (title, author, year)
- [x] Paper cards with metadata
- [x] Paper detail page with full info
- [x] Like/unlike functionality
- [x] Share and Export citation features
- [x] Recommendations page with match scores
- [x] Profile page with settings
- [x] Responsive navigation header

### Database
- [x] Neo4j cloud connection
- [x] SQLite user database
- [x] Sample data seeded (15 papers, 21 citations)

## Prioritized Backlog

### P0 (Critical) - DONE
- All core features implemented

### P1 (High Priority)
- [ ] Load full Neo4j dump file with real papers
- [ ] Pagination for search results
- [ ] Paper PDF viewing integration

### P2 (Medium Priority)
- [ ] User-to-user paper sharing
- [ ] Paper collections/folders
- [ ] Advanced filters (venue, citation count)
- [ ] Export to bibliography formats (BibTeX)

### P3 (Nice to Have)
- [ ] Paper annotations
- [ ] Research reading lists
- [ ] Collaboration features
- [ ] API rate limiting

## Next Tasks
1. Import full Neo4j dump file for complete paper database
2. Add pagination for large result sets
3. Implement BibTeX export format
4. Add paper collections feature

## Technical Notes
- Frontend proxy configured to route `/api` to backend port 8001
- Neo4j connection with fallback to local instance
- JWT tokens expire in 24 hours
- All clipboard operations have fallbacks for browser compatibility
