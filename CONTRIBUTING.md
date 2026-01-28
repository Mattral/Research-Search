# Contributing to ReSearch

Thank you for considering contributing to ReSearch! This document provides guidelines and information to make the contribution process smooth and effective.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Requesting Features](#requesting-features)

---

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

---

## How Can I Contribute?

### Good First Issues

Look for issues tagged with `good first issue` — these are intentionally scoped for newcomers:

- Documentation improvements
- UI/UX tweaks (colors, spacing, responsiveness)
- Adding new arXiv category mappings
- Writing tests for existing endpoints
- Improving error messages

### Areas We Need Help

| Area | Examples |
|------|----------|
| **Frontend** | New pages, component improvements, accessibility |
| **Backend** | New API endpoints, performance optimization |
| **arXiv Integration** | Better search parsing, category expansion |
| **AI/ML** | Better summarization prompts, recommendation algorithms |
| **DevOps** | CI/CD pipelines, monitoring, deployment scripts |
| **Documentation** | Tutorials, API examples, architecture diagrams |
| **Testing** | Unit tests, integration tests, E2E tests |

---

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+ with Yarn
- Git

### 1. Fork and clone

```bash
git clone https://github.com/YOUR_USERNAME/research-paper-discovery.git
cd research-paper-discovery
```

### 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Copy and edit environment variables
cp .env.example .env
# Edit .env with your credentials

# Run the backend
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### 3. Frontend

```bash
cd frontend
yarn install

# Set backend URL
echo "REACT_APP_BACKEND_URL=http://localhost:8001" > .env

# Run the frontend
yarn start
```

### 4. Verify

- Backend API docs: http://localhost:8001/docs
- Frontend: http://localhost:3000

### Using Docker (alternative)

```bash
docker-compose up --build
```

---

## Project Structure

```
backend/
├── db/           # Database connections
├── models/       # SQLAlchemy ORM models
├── routes/       # FastAPI route handlers (one file per domain)
├── schemas/      # Pydantic validation models
├── services/     # Business logic (one file per domain)
└── server.py     # App entry point

frontend/src/
├── components/   # Reusable UI components
├── hooks/        # Custom React hooks
├── lib/          # API client, utilities
└── pages/        # Page-level components (one per route)
```

### Key Conventions

- **Backend routes** are in `routes/` and prefixed with `/api/`
- **Business logic** lives in `services/`, not in route handlers
- **Database queries** use SQLAlchemy ORM (SQL) or raw Cypher (Neo4j)
- **Frontend pages** are in `pages/`, one component per route
- **API client** is centralized in `lib/api.js`

---

## Coding Standards

### Python (Backend)

- **Formatter**: Use `black` with default settings
- **Linter**: Use `ruff` or `flake8`
- **Type hints**: Required for function parameters and return types
- **Docstrings**: Required for all public functions
- **Naming**: `snake_case` for functions/variables, `PascalCase` for classes

```python
# Good
async def search_arxiv(query: str, max_results: int = 20) -> Dict[str, Any]:
    """Search arXiv papers by query string."""
    ...

# Bad
def searchArxiv(q, n=20):
    ...
```

### JavaScript/React (Frontend)

- **Framework**: React 18 with functional components and hooks
- **Styling**: Tailwind CSS utility classes (no inline styles)
- **State**: React hooks (`useState`, `useEffect`, `useCallback`)
- **Naming**: `PascalCase` for components, `camelCase` for functions/variables
- **Testing IDs**: Every interactive element must have `data-testid`

```jsx
// Good
const ArxivSearchPage = () => {
  const [loading, setLoading] = useState(false);
  return <Button data-testid="search-btn">Search</Button>;
};

// Bad
class SearchPage extends Component { ... }
```

### Git Branch Naming

```
feature/arxiv-category-filter
fix/search-pagination-offset
docs/contributing-guide
test/arxiv-service-unit-tests
```

---

## Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <description>

[optional body]
```

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, no code change |
| `refactor` | Code restructuring, no feature change |
| `test` | Adding or updating tests |
| `chore` | Build process, tooling |

### Examples

```
feat(arxiv): add date range filter to search
fix(auth): handle expired JWT tokens gracefully
docs(readme): add Docker setup instructions
test(arxiv): add unit tests for XML parser
```

---

## Pull Request Process

### Before submitting

1. **Create an issue first** for non-trivial changes
2. **Branch from `main`** using the naming convention above
3. **Write tests** for new features and bug fixes
4. **Update documentation** if you change APIs or add features
5. **Run linters** before committing:

```bash
# Backend
cd backend && black . && ruff check .

# Frontend
cd frontend && yarn lint
```

### PR checklist

- [ ] Code follows the project's coding standards
- [ ] Self-reviewed the diff for obvious issues
- [ ] Added/updated tests for changed functionality
- [ ] Updated documentation (README, docstrings, API docs)
- [ ] All existing tests pass
- [ ] Commit messages follow conventional commits
- [ ] PR description explains **what** and **why**

### Review process

1. Submit your PR against `main`
2. A maintainer will review within 48 hours
3. Address review feedback with new commits (don't force-push)
4. Once approved, a maintainer will merge

---

## Reporting Bugs

### Before reporting

1. Search existing issues to avoid duplicates
2. Try reproducing with the latest `main` branch

### Bug report template

```markdown
**Description**: [Clear description of the bug]

**Steps to reproduce**:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**: [What should happen]

**Actual behavior**: [What actually happens]

**Environment**:
- OS: [e.g., macOS 14, Ubuntu 22.04]
- Browser: [e.g., Chrome 120]
- Python version: [e.g., 3.11.5]
- Node version: [e.g., 18.19.0]

**Screenshots**: [If applicable]
```

---

## Requesting Features

### Feature request template

```markdown
**Problem**: [What problem does this solve?]

**Proposed solution**: [How should it work?]

**Alternatives considered**: [Other approaches you've thought of]

**Additional context**: [Screenshots, mockups, related issues]
```

### Feature priority

Features are prioritized by:
1. Impact on core user workflow
2. Number of users affected
3. Implementation complexity
4. Alignment with project roadmap

---

## Environment Variables Reference

### Backend (`backend/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL or SQLite connection string |
| `NEO4J_URI` | No | Neo4j connection URI (graph features disabled without) |
| `NEO4J_USER` | No | Neo4j username |
| `NEO4J_PASSWORD` | No | Neo4j password |
| `JWT_SECRET` | Yes | Secret key for JWT token signing |
| `JWT_ALGORITHM` | No | JWT algorithm (default: HS256) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | Token expiry (default: 1440) |
| `GEMINI_API_KEY` | No | Google Gemini API key for AI summaries |
| `EMERGENT_LLM_KEY` | No | Alternative LLM key |

### Frontend (`frontend/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `REACT_APP_BACKEND_URL` | Yes | Backend API URL |

---

## Thank You

Every contribution matters — whether it's fixing a typo, reporting a bug, or building a new feature. ReSearch is built by researchers for researchers, and your help makes it better for everyone.
