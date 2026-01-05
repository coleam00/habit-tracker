# Habit Tracker

A personal habit tracking web application with streak tracking and completion rate metrics.

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy, SQLite, structlog
- **Frontend**: React 18, Vite, Tailwind CSS, TanStack Query
- **Testing**: pytest, Vitest, Playwright
- **No authentication** - local single-user application

## Project Structure

```
habit-tracker/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI entry point
│   │   ├── database.py       # SQLite connection
│   │   ├── models.py         # SQLAlchemy models
│   │   ├── schemas.py        # Pydantic schemas
│   │   ├── logging_config.py # structlog configuration
│   │   └── routers/          # API endpoints
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── features/         # Feature modules
│   │   ├── api/              # API client
│   │   └── App.jsx
│   └── package.json
├── tests/
│   ├── unit/                 # Unit tests
│   ├── integration/          # API integration tests
│   └── e2e/                  # Playwright E2E tests
└── .claude/
    ├── PRD.md                # Product requirements
    └── reference/            # Best practices docs
```

## Commands

```bash
# Backend
cd backend && uv sync
uv run uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend && npm install && npm run dev

# Testing (Backend)
cd backend
uv run pytest tests/test_streak.py -v        # Unit tests
uv run pytest tests/ -v                       # All tests
uv run pytest --cov=app                       # With coverage

# Testing (Frontend)
npx playwright test                           # E2E tests
```

## MCP Servers

**Playwright MCP** is available for browser automation and E2E testing:
```bash
claude mcp add playwright npx @playwright/mcp@latest
```

Use Playwright MCP for:
- Running and debugging E2E tests
- Visual regression testing
- Browser automation tasks

## Reference Documentation

Read these documents when working on specific areas:

| Document | When to Read |
|----------|--------------|
| `.claude/PRD.md` | Understanding requirements, features, API spec |
| `.claude/reference/fastapi-best-practices.md` | Building API endpoints, Pydantic schemas, dependencies |
| `.claude/reference/sqlite-best-practices.md` | Database schema, queries, SQLAlchemy patterns |
| `.claude/reference/react-frontend-best-practices.md` | Components, hooks, state management, forms |
| `.claude/reference/testing-and-logging.md` | structlog setup, unit/integration/E2E testing patterns |
| `.claude/reference/deployment-best-practices.md` | Docker, production builds, deployment |

## Code Conventions

### Backend (Python)
- Use Pydantic models for all request/response schemas
- Separate schemas: `HabitCreate`, `HabitUpdate`, `HabitResponse`
- Use `Depends()` for database sessions and validation
- Store dates as ISO-8601 TEXT in SQLite (`YYYY-MM-DD`)
- Enable foreign keys via PRAGMA on every connection

### Frontend (React)
- Feature-based folder structure under `src/features/`
- Use TanStack Query for all API calls (no raw useEffect fetching)
- Tailwind CSS for styling - no separate CSS files
- Forms with react-hook-form + Zod validation

### API Design
- RESTful endpoints under `/api/`
- Return 201 for POST, 204 for DELETE
- Use HTTPException with descriptive error codes

## Logging

Use **structlog** for all logging. Configure at app startup:
- Development: Pretty console output with colors
- Production: JSON format for log aggregation

```python
import structlog
logger = structlog.get_logger()

# Bind context for all subsequent logs
structlog.contextvars.bind_contextvars(request_id=request_id)

# Log with structured data
logger.info("Habit completed", habit_id=1, streak=5)
```

Request logging middleware automatically logs:
- Request ID, method, path
- Response status code and duration

## Database

SQLite with WAL mode. Always run these PRAGMAs on connection:
```sql
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;
PRAGMA synchronous=NORMAL;
```

Two tables: `habits` and `completions`. See `.claude/PRD.md` for schema.

## Testing Strategy

### Testing Pyramid
- **70% Unit tests**: Pure functions, business logic, validators
- **20% Integration tests**: API endpoints with real database
- **10% E2E tests**: Critical user journeys with Playwright

### Unit Tests
- Test streak calculation, date utilities, validators
- Mock external dependencies
- Fast execution (milliseconds)

### Integration Tests
- Test API endpoints with in-memory SQLite
- Use `TestClient` and dependency overrides
- Test success and error cases

### E2E Tests
- Use Playwright with Page Object Model
- Test critical flows: create habit, complete habit, view calendar
- Run visual regression tests for UI consistency

### Test Organization
```
tests/
├── conftest.py              # Shared fixtures
├── unit/
│   └── test_streak.py       # Business logic tests
├── integration/
│   └── test_api_habits.py   # API tests with real DB
└── e2e/
    ├── pages/               # Page objects
    └── habits.spec.js       # User journey tests
```
