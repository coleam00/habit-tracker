# FastAPI Best Practices Reference

A concise reference guide for building production-ready FastAPI applications.

---

## Table of Contents

1. [Project Structure](#1-project-structure)
2. [Routing & Endpoints](#2-routing--endpoints)
3. [Pydantic Models & Validation](#3-pydantic-models--validation)
4. [Dependency Injection](#4-dependency-injection)
5. [Error Handling](#5-error-handling)
6. [Database Integration](#6-database-integration)
7. [Performance & Async](#7-performance--async)
8. [Testing](#8-testing)
9. [Security](#9-security)
10. [Configuration](#10-configuration)
11. [Anti-Patterns](#11-anti-patterns)

---

## 1. Project Structure

### Small Projects (File-Type Structure)

```
app/
├── main.py           # FastAPI app instance
├── routers/          # API route handlers
├── models.py         # SQLAlchemy models
├── schemas.py        # Pydantic schemas
├── database.py       # Database configuration
├── dependencies.py   # Shared dependencies
└── config.py         # Settings
```

### Larger Projects (Domain-Based Structure)

```
src/
├── habits/
│   ├── router.py
│   ├── schemas.py
│   ├── models.py
│   ├── service.py
│   ├── dependencies.py
│   └── exceptions.py
├── completions/
│   └── (same structure)
├── shared/
│   ├── config.py
│   ├── database.py
│   └── exceptions.py
└── main.py
```

### Key Principles

- **Separation of concerns**: Keep routing, models, schemas, services separate
- **One router per domain**: Group related endpoints together
- **Explicit imports**: Use full module paths when importing across packages

```python
# Good: Explicit imports
from src.habits import service as habits_service
from src.habits import constants as habits_constants

# Avoid: Ambiguous imports
from src.habits.service import *
```

---

## 2. Routing & Endpoints

### Using APIRouter

```python
from fastapi import APIRouter, Depends, status

router = APIRouter(
    prefix="/habits",
    tags=["habits"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=list[HabitResponse])
async def list_habits():
    pass

@router.post("/", response_model=HabitResponse, status_code=status.HTTP_201_CREATED)
async def create_habit(habit: HabitCreate):
    pass
```

### Include in Main App

```python
from fastapi import FastAPI
from .routers import habits, completions

app = FastAPI()
app.include_router(habits.router, prefix="/api")
app.include_router(completions.router, prefix="/api")
```

### Path vs Query Parameters

```python
from typing import Annotated
from fastapi import Path, Query

@router.get("/habits/{habit_id}")
async def get_habit(
    # Path parameter: resource identification
    habit_id: Annotated[int, Path(ge=1, description="Habit ID")],
    # Query parameter: filtering/options
    include_stats: Annotated[bool, Query()] = False,
):
    pass
```

**Rule of thumb**:
- Path parameters for resource identification: `/habits/{id}`
- Query parameters for filtering, sorting, pagination: `/habits?status=active&page=1`

### Response Models and Status Codes

```python
from fastapi import status
from fastapi.responses import JSONResponse

@router.post("/", response_model=HabitResponse, status_code=status.HTTP_201_CREATED)
async def create_habit(habit: HabitCreate):
    return created_habit

@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_habit(habit_id: int):
    return None  # 204 has no body

@router.get("/{habit_id}")
async def get_habit(habit_id: int):
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    return habit
```

### API Versioning

```python
# URL path versioning (recommended)
app.include_router(v1_router, prefix="/api/v1")
app.include_router(v2_router, prefix="/api/v2")

# Or using sub-applications
v1_app = FastAPI()
v2_app = FastAPI()
app.mount("/api/v1", v1_app)
app.mount("/api/v2", v2_app)
```

---

## 3. Pydantic Models & Validation

### Base Schema Pattern

```python
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # For ORM compatibility
```

### Request/Response Schema Pattern

```python
from pydantic import BaseModel, Field

# Shared attributes
class HabitBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None

# Create schema - what client sends
class HabitCreate(HabitBase):
    color: str = Field(default="#10B981", pattern=r"^#[0-9A-Fa-f]{6}$")

# Update schema - all fields optional
class HabitUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")

# Response schema - includes DB fields, excludes sensitive data
class HabitResponse(HabitBase):
    id: int
    color: str
    created_at: datetime
    current_streak: int
    completion_rate: float

    model_config = ConfigDict(from_attributes=True)
```

### Field Validation

```python
from pydantic import BaseModel, Field, field_validator, model_validator

class HabitCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    target_days: list[str] = Field(default_factory=list)

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be blank")
        return v.strip()

    @field_validator("target_days")
    @classmethod
    def validate_days(cls, v: list[str]) -> list[str]:
        valid_days = {"mon", "tue", "wed", "thu", "fri", "sat", "sun"}
        for day in v:
            if day.lower() not in valid_days:
                raise ValueError(f"Invalid day: {day}")
        return [d.lower() for d in v]

    @model_validator(mode="after")
    def check_consistency(self):
        # Cross-field validation
        return self
```

### Nested Models

```python
class CompletionResponse(BaseModel):
    date: str
    status: str
    notes: str | None

class HabitDetailResponse(HabitResponse):
    completions: list[CompletionResponse]
    longest_streak: int
```

### OpenAPI Examples

```python
class HabitCreate(BaseModel):
    name: str
    description: str | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "Morning Exercise",
                    "description": "30 minutes of cardio",
                }
            ]
        }
    )
```

---

## 4. Dependency Injection

### Basic Dependencies

```python
from fastapi import Depends

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/habits")
def list_habits(db: Session = Depends(get_db)):
    return db.query(Habit).all()
```

### Validation Dependencies

```python
from fastapi import Depends, HTTPException

async def valid_habit_id(habit_id: int, db: Session = Depends(get_db)) -> Habit:
    habit = db.query(Habit).filter(Habit.id == habit_id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    return habit

@router.get("/habits/{habit_id}")
async def get_habit(habit: Habit = Depends(valid_habit_id)):
    return habit  # Already validated and fetched

@router.delete("/habits/{habit_id}")
async def delete_habit(habit: Habit = Depends(valid_habit_id), db: Session = Depends(get_db)):
    db.delete(habit)
    db.commit()
```

### Chained Dependencies

```python
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    # Decode and validate token
    return user

async def get_current_active_user(user: User = Depends(get_current_user)) -> User:
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user

@router.get("/me")
async def read_current_user(user: User = Depends(get_current_active_user)):
    return user
```

### Class-Based Dependencies

```python
class Pagination:
    def __init__(self, skip: int = 0, limit: int = Query(default=100, le=100)):
        self.skip = skip
        self.limit = limit

@router.get("/habits")
async def list_habits(pagination: Pagination = Depends()):
    return habits[pagination.skip : pagination.skip + pagination.limit]
```

### Key Points

- Dependencies are **cached within a request** by default
- Use `Depends(dep, use_cache=False)` to disable caching
- Use `async def` for dependencies when possible
- Dependencies can depend on other dependencies (chain them)

---

## 5. Error Handling

### HTTPException

```python
from fastapi import HTTPException, status

@router.get("/habits/{habit_id}")
async def get_habit(habit_id: int):
    habit = get_habit_by_id(habit_id)
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found",
            headers={"X-Error-Code": "HABIT_NOT_FOUND"},
        )
    return habit
```

### Custom Exception Classes

```python
# exceptions.py
class AppException(Exception):
    def __init__(self, status_code: int, detail: str, error_code: str):
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code

class HabitNotFoundError(AppException):
    def __init__(self, habit_id: int):
        super().__init__(
            status_code=404,
            detail=f"Habit with ID {habit_id} not found",
            error_code="HABIT_NOT_FOUND",
        )

class DuplicateCompletionError(AppException):
    def __init__(self, habit_id: int, date: str):
        super().__init__(
            status_code=409,
            detail=f"Completion already exists for habit {habit_id} on {date}",
            error_code="DUPLICATE_COMPLETION",
        )
```

### Global Exception Handlers

```python
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_code,
            "detail": exc.detail,
            "path": str(request.url),
        },
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": "VALIDATION_ERROR",
            "detail": exc.errors(),
        },
    )
```

### Consistent Error Response Format

```json
{
    "error": "HABIT_NOT_FOUND",
    "detail": "Habit with ID 123 not found",
    "path": "/api/habits/123"
}
```

---

## 6. Database Integration

### SQLAlchemy Setup

```python
# database.py
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./habits.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite only
)

# Apply PRAGMA settings for SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

### Model Definition

```python
# models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

class Habit(Base):
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    color = Column(String(7), default="#10B981")
    created_at = Column(DateTime, default=datetime.utcnow)
    archived_at = Column(DateTime, nullable=True)

    completions = relationship(
        "Completion",
        back_populates="habit",
        cascade="all, delete-orphan",
        lazy="selectin",  # Good for collections
    )

class Completion(Base):
    __tablename__ = "completions"

    id = Column(Integer, primary_key=True, index=True)
    habit_id = Column(Integer, ForeignKey("habits.id", ondelete="CASCADE"), nullable=False, index=True)
    completed_date = Column(String(10), nullable=False)  # YYYY-MM-DD
    status = Column(String(10), default="completed")  # completed, skipped
    notes = Column(Text)

    habit = relationship("Habit", back_populates="completions")

    __table_args__ = (
        UniqueConstraint("habit_id", "completed_date", name="uq_habit_date"),
    )
```

### Dependency with Context Manager

```python
from typing import Generator
from sqlalchemy.orm import Session

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Repository Pattern (Optional)

```python
# repositories/habits.py
class HabitRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, habit_id: int) -> Habit | None:
        return self.db.query(Habit).filter(Habit.id == habit_id).first()

    def get_all(self, include_archived: bool = False) -> list[Habit]:
        query = self.db.query(Habit)
        if not include_archived:
            query = query.filter(Habit.archived_at.is_(None))
        return query.all()

    def create(self, data: HabitCreate) -> Habit:
        habit = Habit(**data.model_dump())
        self.db.add(habit)
        self.db.commit()
        self.db.refresh(habit)
        return habit
```

### Eager Loading

```python
from sqlalchemy.orm import joinedload, selectinload

# For many-to-one relationships
habit = db.query(Habit).options(joinedload(Habit.category)).first()

# For one-to-many collections
habits = db.query(Habit).options(selectinload(Habit.completions)).all()
```

---

## 7. Performance & Async

### Async vs Sync Functions

| Work Type | Function Definition | Reason |
|-----------|---------------------|--------|
| Async I/O (DB, HTTP) | `async def` | Non-blocking |
| Sync/blocking I/O | `def` | Runs in threadpool |
| CPU-bound | External worker | Avoids blocking |

```python
# GOOD: Async for I/O operations
@router.get("/habits")
async def list_habits(db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Habit))
    return result.scalars().all()

# GOOD: Sync for blocking operations (FastAPI handles threadpool)
@router.get("/file")
def read_file():
    with open("file.txt") as f:
        return f.read()

# BAD: Blocking call in async function
@router.get("/bad")
async def bad_endpoint():
    time.sleep(5)  # Blocks entire event loop!
    return {"status": "done"}
```

### Background Tasks

```python
from fastapi import BackgroundTasks

def send_notification(email: str, message: str):
    # Long-running task
    pass

@router.post("/habits")
async def create_habit(habit: HabitCreate, background_tasks: BackgroundTasks):
    created_habit = create_habit_in_db(habit)
    background_tasks.add_task(send_notification, "user@example.com", "Habit created!")
    return created_habit
```

### Caching

```python
from functools import lru_cache

# Cache settings (called once)
@lru_cache
def get_settings():
    return Settings()

# For Redis caching, use fastapi-cache
from fastapi_cache.decorator import cache

@router.get("/stats")
@cache(expire=60)
async def get_stats():
    return calculate_expensive_stats()
```

---

## 8. Testing

### Basic Test Setup

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    with SessionLocal() as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session):
    def get_session_override():
        return session

    app.dependency_overrides[get_db] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
```

### Writing Tests

```python
# tests/test_habits.py
def test_create_habit(client):
    response = client.post(
        "/api/habits",
        json={"name": "Exercise", "description": "Daily workout"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Exercise"
    assert "id" in data

def test_create_habit_validation_error(client):
    response = client.post("/api/habits", json={"name": ""})
    assert response.status_code == 422

def test_get_habit_not_found(client):
    response = client.get("/api/habits/999")
    assert response.status_code == 404

def test_list_habits(client, session):
    # Setup
    habit = Habit(name="Test Habit")
    session.add(habit)
    session.commit()

    # Test
    response = client.get("/api/habits")
    assert response.status_code == 200
    assert len(response.json()) == 1
```

### Async Testing

```python
import pytest
from httpx import AsyncClient, ASGITransport

@pytest.mark.anyio
async def test_async_endpoint():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/api/habits")
        assert response.status_code == 200
```

---

## 9. Security

### Input Validation

FastAPI + Pydantic handles most validation. Additional measures:

```python
from pydantic import BaseModel, Field, field_validator
import bleach

class CommentCreate(BaseModel):
    content: str = Field(..., max_length=1000)

    @field_validator("content")
    @classmethod
    def sanitize_content(cls, v: str) -> str:
        return bleach.clean(v)  # Remove XSS vectors
```

### CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Specific origins, not "*"
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

### SQL Injection Prevention

```python
# GOOD: Use ORM
habit = db.query(Habit).filter(Habit.id == habit_id).first()

# GOOD: Parameterized queries
result = db.execute(text("SELECT * FROM habits WHERE id = :id"), {"id": habit_id})

# BAD: String formatting (VULNERABLE!)
db.execute(f"SELECT * FROM habits WHERE id = {habit_id}")  # NEVER DO THIS
```

### Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/habits")
@limiter.limit("100/minute")
async def list_habits(request: Request):
    pass
```

---

## 10. Configuration

### Using Pydantic Settings

```python
# config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "Habit Tracker"
    database_url: str = "sqlite:///./habits.db"
    debug: bool = False
    cors_origins: list[str] = ["http://localhost:5173"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()
```

### Usage

```python
from .config import get_settings

settings = get_settings()
print(settings.database_url)
```

### .env File

```env
DATABASE_URL=sqlite:///./habits.db
DEBUG=true
CORS_ORIGINS=["http://localhost:5173"]
```

---

## 11. Anti-Patterns

### Critical Anti-Patterns to Avoid

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Blocking I/O in `async def` | Halts event loop | Use async libs or plain `def` |
| Endpoint-to-endpoint calls | Tight coupling | Use service layer |
| Global mutable state | Race conditions | Use Redis/database |
| Returning ORM objects | Exposes internals | Use response schemas |
| Not using Pydantic | Missing validation | Always define schemas |
| String-formatted SQL | SQL injection | Use ORM or parameterized queries |
| Hardcoded config | Inflexible | Use environment variables |

### Common Mistakes

```python
# BAD: Blocking in async
async def bad():
    time.sleep(5)  # Blocks event loop

# BAD: Not closing connections
def bad_db():
    return SessionLocal()  # Never closed!

# BAD: Sharing session between requests
db = SessionLocal()  # Global session - race conditions!

# BAD: Exposing internal model
@router.get("/habits")
def list_habits(db: Session = Depends(get_db)):
    return db.query(Habit).all()  # Returns ORM objects

# GOOD: Use response model
@router.get("/habits", response_model=list[HabitResponse])
def list_habits(db: Session = Depends(get_db)):
    return db.query(Habit).all()  # Serialized via Pydantic
```

---

## Lifespan Events

### Modern Pattern (Recommended)

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up...")
    # Initialize resources (db pools, caches, etc.)
    yield
    # Shutdown
    print("Shutting down...")
    # Cleanup resources

app = FastAPI(lifespan=lifespan)
```

---

## Quick Reference

### HTTP Status Codes

| Code | Constant | Use Case |
|------|----------|----------|
| 200 | `HTTP_200_OK` | Successful GET, PUT |
| 201 | `HTTP_201_CREATED` | Successful POST |
| 204 | `HTTP_204_NO_CONTENT` | Successful DELETE |
| 400 | `HTTP_400_BAD_REQUEST` | Invalid request |
| 404 | `HTTP_404_NOT_FOUND` | Resource not found |
| 409 | `HTTP_409_CONFLICT` | Duplicate resource |
| 422 | `HTTP_422_UNPROCESSABLE_ENTITY` | Validation error |
| 500 | `HTTP_500_INTERNAL_SERVER_ERROR` | Server error |

### Common Imports

```python
from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, Query, Path, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator, ConfigDict
from sqlalchemy.orm import Session
from typing import Annotated
```

---

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [FastAPI Best Practices (GitHub)](https://github.com/zhanymkanov/fastapi-best-practices)
