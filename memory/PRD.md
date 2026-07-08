# ReSearch — PRD (Product Requirements Document)

## Original Problem Statement
Upgrade features using arXiv public API. Add proper documentation, architecture documentation, Docker/Kubernetes setups. Make contributor-friendly. Explain what/who/why/how/benefit.

Follow-up: Transform into world-class research platform with multi-source search, paper comparison, workspaces, annotations, trend visualization, exports, and comprehensive documentation.

## Architecture
- **Frontend**: React 18 + Tailwind CSS (dark academic theme)
- **Backend**: FastAPI (Python 3.11)
- **Databases**: PostgreSQL/SQLite (users, workspaces, reading lists) + Neo4j (graph recommendations)
- **External APIs**: arXiv, Semantic Scholar, OpenAlex
- **AI**: Google Gemini via Emergent LLM key
- **DevOps**: Docker Compose + Kubernetes manifests

## User Personas
1. **Graduate students** — Literature review, paper discovery, reading lists
2. **Researchers** — Multi-source search, trend analysis, paper comparison
3. **Professors** — Category monitoring, curated collections
4. **Independent learners** — AI summaries, guided exploration

## Core Requirements
- Multi-source search (arXiv + Semantic Scholar + OpenAlex)
- AI paper summarization (Gemini)
- Paper comparison (2-5 papers) with AI analysis
- Workspaces with annotations and tags
- Export (BibTeX, Markdown)
- Publication trend visualization
- arXiv category browsing and latest papers feed
- Reading list (save/unsave)
- JWT authentication
- Dark academic theme
- Docker + Kubernetes deployment

## What's Been Implemented (Jan 2026)

### Phase 1 - arXiv Integration
- arXiv search service (XML parser, HTTPS, category support)
- arXiv routes (search, categories, latest, paper detail, save, reading list)
- AI summarization service (Gemini via Emergent LLM key)
- SavedArxivPaper model
- Frontend pages: ArxivSearchPage, ArxivPaperPage, ReadingListPage, LatestPapersPage
- Dark academic theme (Crimson Pro + DM Sans fonts)
- Updated Header with new navigation

### Phase 2 - World-Class Upgrade
- Multi-source search (Semantic Scholar + OpenAlex services)
- Discover page (unified search across 3 sources)
- Paper comparison (side-by-side matrix + AI comparison)
- Trend visualization (10-year chart via OpenAlex)
- Workspaces CRUD + paper management
- Annotations (notes + tags per paper)
- Export (BibTeX + Markdown)
- Compare page, WorkspacesPage, WorkspaceDetailPage

### Phase 3 - Documentation & DevOps
- World-class README.md
- CONTRIBUTING.md with coding standards, PR process
- CODE_OF_CONDUCT.md
- LICENSE (MIT)
- Architecture.md (detailed system architecture)
- Dockerfile.backend, Dockerfile.frontend
- docker-compose.yml
- Kubernetes manifests (namespace, secrets, postgres, backend, frontend, ingress)
- GitHub templates (bug report, feature request, PR template)
- .env.example files
- .gitignore

## Testing
- Iteration 1: 100% backend (17/17), 95% frontend
- Iteration 2: 100% backend (13/13), 85% frontend (core working)

## Backlog (P0-P2)
### P0 (Next)
- Semantic/embedding-based search ranking
- User feedback (thumbs up/down) for relevance
- Shared workspaces & team annotations

### P1
- PDF viewer with inline highlighting
- Topic clustering visualization
- Citation network graph explorer
- Zotero/Mendeley export

### P2
- CLI tool for automation
- Plugin architecture
- Notion/Obsidian integration
- Author impact analysis
- Method/dataset extraction from papers
