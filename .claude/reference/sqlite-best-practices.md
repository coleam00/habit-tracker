# SQLite & SQL Best Practices Reference

A concise reference guide for working with SQLite databases in Python applications.

---

## Table of Contents

1. [When to Use SQLite](#1-when-to-use-sqlite)
2. [Schema Design](#2-schema-design)
3. [Data Types](#3-data-types)
4. [Indexing](#4-indexing)
5. [Query Optimization](#5-query-optimization)
6. [SQLAlchemy Patterns](#6-sqlalchemy-patterns)
7. [Data Integrity](#7-data-integrity)
8. [Transactions](#8-transactions)
9. [Python Integration](#9-python-integration)
10. [Performance Tuning](#10-performance-tuning)
11. [Backup & Recovery](#11-backup--recovery)
12. [Anti-Patterns](#12-anti-patterns)

---

## 1. When to Use SQLite

### Ideal Use Cases

- **Embedded/IoT devices**: Mobile apps, desktop apps, local tools
- **Application file format**: Single-file database for app data
- **Low-to-medium traffic websites**: Under 100K requests/day
- **Development and testing**: Quick setup, no server needed
- **Data analysis**: Import CSV, run SQL queries
- **Caching layer**: Local cache of remote data
- **Single-user applications**: Personal tools, local apps

### When NOT to Use SQLite

- **High write concurrency**: SQLite allows one writer at a time
- **Network filesystems**: NFS, SMB can cause corruption
- **Multiple servers**: Can't share SQLite across machines
- **Very large datasets**: >1TB may need distributed solutions
- **High-traffic production**: Consider PostgreSQL instead

### Key Characteristics

| Feature | Value |
|---------|-------|
| Library size | <600KB |
| Max database size | 281 TB |
| Max row size | 1 GB |
| Concurrent readers | Unlimited |
| Concurrent writers | 1 |
| ACID compliant | Yes |

---

## 2. Schema Design

### Primary Keys

```sql
-- Recommended: INTEGER PRIMARY KEY (aliases to rowid, auto-increments)
CREATE TABLE habits (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL
);

-- With explicit AUTOINCREMENT (prevents rowid reuse after deletion)
CREATE TABLE habits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

-- Composite primary key
CREATE TABLE completions (
    habit_id INTEGER NOT NULL,
    completed_date TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'completed',
    PRIMARY KEY (habit_id, completed_date)
);
```

### Foreign Keys

```sql
-- Foreign keys are DISABLED by default - must enable per connection
PRAGMA foreign_keys = ON;

CREATE TABLE completions (
    id INTEGER PRIMARY KEY,
    habit_id INTEGER NOT NULL,
    completed_date TEXT NOT NULL,
    FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE
);
```

**Cascading actions**:

| Action | Behavior |
|--------|----------|
| `NO ACTION` | Reject if child rows exist (default) |
| `CASCADE` | Delete/update child rows |
| `SET NULL` | Set foreign key to NULL |
| `SET DEFAULT` | Set foreign key to default value |
| `RESTRICT` | Like NO ACTION but immediate |

### Table Constraints

```sql
CREATE TABLE habits (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    color TEXT DEFAULT '#10B981',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    archived_at TEXT,

    -- Check constraint
    CHECK (length(name) > 0),
    CHECK (color GLOB '#[0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f]')
);

CREATE TABLE completions (
    id INTEGER PRIMARY KEY,
    habit_id INTEGER NOT NULL,
    completed_date TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'completed',

    FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE,
    UNIQUE (habit_id, completed_date),
    CHECK (status IN ('completed', 'skipped'))
);
```

### WITHOUT ROWID Tables

```sql
-- Use for non-integer or composite primary keys
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
) WITHOUT ROWID;
```

**When to use**:
- Non-integer primary keys
- Composite primary keys
- Small row sizes
- Frequent primary key lookups

**When to avoid**:
- Large primary keys (duplicated in all indexes)
- Many secondary indexes
- Large row sizes

---

## 3. Data Types

### SQLite Type Affinity

SQLite uses dynamic typing - the type is associated with values, not columns.

**Five storage classes**:

| Class | Description |
|-------|-------------|
| `NULL` | NULL value |
| `INTEGER` | Signed integer (1-8 bytes) |
| `REAL` | 8-byte IEEE float |
| `TEXT` | UTF-8/UTF-16 string |
| `BLOB` | Binary data |

**Type affinity rules** (based on declared type name):
1. Contains "INT" → INTEGER
2. Contains "CHAR", "CLOB", "TEXT" → TEXT
3. Contains "BLOB" or no type → BLOB
4. Contains "REAL", "FLOA", "DOUB" → REAL
5. Otherwise → NUMERIC

### Date/Time Storage

**Option 1: TEXT (ISO 8601) - Recommended**

```sql
CREATE TABLE completions (
    id INTEGER PRIMARY KEY,
    completed_date TEXT NOT NULL,  -- 'YYYY-MM-DD'
    created_at TEXT NOT NULL DEFAULT (datetime('now'))  -- 'YYYY-MM-DD HH:MM:SS'
);

-- Query examples
SELECT * FROM completions WHERE completed_date = '2025-01-15';
SELECT * FROM completions WHERE completed_date >= '2025-01-01' AND completed_date < '2025-02-01';
SELECT * FROM completions WHERE completed_date BETWEEN '2025-01-01' AND '2025-01-31';
```

**Benefits**: Human-readable, lexicographically sortable, works with SQLite date functions.

**Option 2: INTEGER (Unix timestamp)**

```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY,
    timestamp INTEGER NOT NULL DEFAULT (strftime('%s', 'now'))
);

-- Query examples
SELECT * FROM events WHERE timestamp >= strftime('%s', '2025-01-01');
SELECT datetime(timestamp, 'unixepoch') as readable_time FROM events;
```

**Benefits**: Smaller storage (8 bytes), faster comparisons.

### Boolean Handling

```sql
-- SQLite has no native BOOLEAN - use INTEGER 0/1
CREATE TABLE habits (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1))
);

-- TRUE and FALSE are aliases for 1 and 0 (SQLite 3.23.0+)
INSERT INTO habits (name, is_active) VALUES ('Exercise', TRUE);
SELECT * FROM habits WHERE is_active = TRUE;
```

### JSON Storage

```sql
-- Store as TEXT, query with JSON functions (SQLite 3.38.0+)
CREATE TABLE habits (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    settings TEXT  -- JSON string
);

INSERT INTO habits (name, settings)
VALUES ('Exercise', '{"reminder_time": "09:00", "notifications": true}');

-- Query JSON
SELECT
    name,
    json_extract(settings, '$.reminder_time') as reminder
FROM habits
WHERE json_extract(settings, '$.notifications') = 1;
```

### STRICT Tables (SQLite 3.37.0+)

```sql
-- Enforce type checking
CREATE TABLE habits (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    count INTEGER NOT NULL
) STRICT;

-- This will fail: INSERT INTO habits (name, count) VALUES ('Test', 'not a number');
```

---

## 4. Indexing

### When to Index

- Columns in `WHERE` clauses
- Columns in `JOIN` conditions
- Columns in `ORDER BY` clauses
- Foreign key columns (critical for CASCADE operations)

### Index Types

```sql
-- Single column index
CREATE INDEX idx_habits_name ON habits(name);

-- Composite index (column order matters!)
CREATE INDEX idx_completions_habit_date ON completions(habit_id, completed_date);

-- Unique index
CREATE UNIQUE INDEX idx_habits_name_unique ON habits(name);

-- Partial index (indexes subset of rows)
CREATE INDEX idx_active_habits ON habits(name) WHERE archived_at IS NULL;

-- Expression index
CREATE INDEX idx_habits_lower_name ON habits(lower(name));
```

### Composite Index Column Order

The order of columns in a composite index matters:

```sql
CREATE INDEX idx_completions ON completions(habit_id, completed_date);

-- Uses index (habit_id is leftmost)
SELECT * FROM completions WHERE habit_id = 1;

-- Uses index (both columns, in order)
SELECT * FROM completions WHERE habit_id = 1 AND completed_date = '2025-01-15';

-- Does NOT use index efficiently (completed_date is not leftmost)
SELECT * FROM completions WHERE completed_date = '2025-01-15';
```

### Covering Indexes

```sql
-- Include all columns needed by query to avoid table lookup
CREATE INDEX idx_completions_covering ON completions(habit_id, completed_date, status);

-- This query is fully satisfied by the index
SELECT completed_date, status FROM completions WHERE habit_id = 1;
```

### Index Trade-offs

| Benefit | Cost |
|---------|------|
| Faster reads | Slower writes |
| Faster ORDER BY | More disk space |
| Faster JOINs | Memory overhead |

**Rule of thumb**: Expect ~5x slower INSERTs per secondary index.

---

## 5. Query Optimization

### EXPLAIN QUERY PLAN

```sql
EXPLAIN QUERY PLAN
SELECT h.name, COUNT(*) as completions
FROM habits h
JOIN completions c ON h.id = c.habit_id
WHERE c.completed_date >= '2025-01-01'
GROUP BY h.id;

-- Output interpretation:
-- SCAN = full table scan (often bad)
-- SEARCH = using index (good)
-- USING INDEX = index-only access (best)
-- USING COVERING INDEX = no table access needed (best)
```

### Query Tips

```sql
-- BAD: SELECT *
SELECT * FROM habits;

-- GOOD: Select only needed columns
SELECT id, name, created_at FROM habits;

-- BAD: LIKE for prefix search without index
SELECT * FROM habits WHERE name LIKE '%exercise%';

-- GOOD: Prefix LIKE can use index
SELECT * FROM habits WHERE name LIKE 'exercise%';

-- BAD: Functions on indexed columns
SELECT * FROM habits WHERE lower(name) = 'exercise';

-- GOOD: Create expression index, or normalize data
CREATE INDEX idx_lower_name ON habits(lower(name));

-- BAD: OR on different columns (hard to optimize)
SELECT * FROM habits WHERE name = 'Exercise' OR description = 'workout';

-- GOOD: Use UNION for complex OR conditions
SELECT * FROM habits WHERE name = 'Exercise'
UNION
SELECT * FROM habits WHERE description = 'workout';
```

### Efficient Date Queries

```sql
-- For TEXT dates (ISO 8601)
SELECT * FROM completions
WHERE completed_date >= '2025-01-01'
  AND completed_date < '2025-02-01';

-- For current month
SELECT * FROM completions
WHERE completed_date >= date('now', 'start of month')
  AND completed_date < date('now', 'start of month', '+1 month');

-- DON'T use LIKE for dates
-- BAD: WHERE completed_date LIKE '2025-01%'
```

### Running ANALYZE

```sql
-- Update statistics for query planner
ANALYZE;

-- Run before closing connections (SQLite 3.18.0+)
PRAGMA optimize;
```

---

## 6. SQLAlchemy Patterns

### Engine Setup

```python
from sqlalchemy import create_engine, event

engine = create_engine(
    "sqlite:///habits.db",
    connect_args={"check_same_thread": False},  # For multi-threaded apps
    echo=False,  # Set True for SQL logging
)

# Apply PRAGMA settings on every connection
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA cache_size=-64000")  # 64MB
    cursor.execute("PRAGMA temp_store=MEMORY")
    cursor.close()
```

### Model Definition

```python
from sqlalchemy import Column, Integer, String, Text, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Habit(Base):
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    color = Column(String(7), default="#10B981")
    created_at = Column(String(19), nullable=False)  # YYYY-MM-DD HH:MM:SS
    archived_at = Column(String(19))

    completions = relationship(
        "Completion",
        back_populates="habit",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        CheckConstraint("length(name) > 0", name="name_not_empty"),
    )


class Completion(Base):
    __tablename__ = "completions"

    id = Column(Integer, primary_key=True)
    habit_id = Column(Integer, ForeignKey("habits.id", ondelete="CASCADE"), nullable=False, index=True)
    completed_date = Column(String(10), nullable=False)  # YYYY-MM-DD
    status = Column(String(10), default="completed")
    notes = Column(Text)

    habit = relationship("Habit", back_populates="completions")

    __table_args__ = (
        UniqueConstraint("habit_id", "completed_date", name="uq_habit_date"),
        CheckConstraint("status IN ('completed', 'skipped')", name="valid_status"),
    )
```

### Relationship Loading Strategies

| Strategy | Use Case |
|----------|----------|
| `lazy="select"` | Default, N+1 if accessed |
| `lazy="joined"` | Many-to-one relationships |
| `lazy="selectin"` | One-to-many collections |
| `lazy="raise"` | Prevent accidental lazy loads |

```python
from sqlalchemy.orm import joinedload, selectinload

# Eager load in query
habits = session.query(Habit).options(selectinload(Habit.completions)).all()

# For many-to-one
completions = session.query(Completion).options(joinedload(Completion.habit)).all()
```

### Session Management

```python
from sqlalchemy.orm import sessionmaker, Session

SessionLocal = sessionmaker(bind=engine)

# Context manager pattern (recommended)
def get_habits():
    with Session(engine) as session:
        return session.query(Habit).all()

# With transaction handling
def create_habit(name: str):
    with Session(engine) as session, session.begin():
        habit = Habit(name=name, created_at=datetime.now().isoformat())
        session.add(habit)
        # Auto-commits on success, rolls back on exception
        return habit

# For FastAPI dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## 7. Data Integrity

### Constraints Summary

```sql
CREATE TABLE example (
    id INTEGER PRIMARY KEY,                    -- Primary key
    name TEXT NOT NULL,                        -- Required field
    email TEXT UNIQUE,                         -- No duplicates
    age INTEGER CHECK (age >= 0),              -- Value validation
    category_id INTEGER REFERENCES categories(id),  -- Foreign key
    status TEXT DEFAULT 'active'               -- Default value
);
```

### Enforcing Foreign Keys

```python
# MUST enable foreign keys per connection
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# Verify it's enabled
result = connection.execute("PRAGMA foreign_keys").fetchone()
assert result[0] == 1
```

### Soft Deletes

```sql
-- Instead of DELETE, set archived_at
UPDATE habits SET archived_at = datetime('now') WHERE id = 1;

-- Query active records
SELECT * FROM habits WHERE archived_at IS NULL;

-- Create partial index for active records
CREATE INDEX idx_active_habits ON habits(name) WHERE archived_at IS NULL;
```

---

## 8. Transactions

### Basic Transactions

```sql
BEGIN TRANSACTION;
INSERT INTO habits (name, created_at) VALUES ('Exercise', datetime('now'));
INSERT INTO completions (habit_id, completed_date) VALUES (last_insert_rowid(), '2025-01-15');
COMMIT;

-- On error
ROLLBACK;
```

### Python Transactions

```python
# Explicit transaction
with engine.begin() as connection:
    connection.execute(text("INSERT INTO habits ..."))
    connection.execute(text("INSERT INTO completions ..."))
    # Auto-commits on success, auto-rollbacks on exception

# SQLAlchemy ORM
with Session(engine) as session, session.begin():
    habit = Habit(name="Exercise")
    session.add(habit)
    completion = Completion(habit=habit, completed_date="2025-01-15")
    session.add(completion)
    # Auto-commits/rollbacks
```

### Isolation Levels

SQLite supports serializable isolation by default. Writers block other writers, but readers never block.

---

## 9. Python Integration

### Connection Basics

```python
import sqlite3

# Context manager (commits on success, but doesn't close!)
with sqlite3.connect("habits.db") as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM habits")
    rows = cursor.fetchall()

# Explicit close
conn = sqlite3.connect("habits.db")
try:
    # ... operations
    conn.commit()
finally:
    conn.close()
```

### Parameterized Queries (SQL Injection Prevention)

```python
# Question mark placeholders
cursor.execute(
    "INSERT INTO habits (name, description) VALUES (?, ?)",
    (name, description)
)

# Named placeholders
cursor.execute(
    "INSERT INTO habits (name, description) VALUES (:name, :desc)",
    {"name": name, "desc": description}
)

# For IN clauses
ids = [1, 2, 3]
placeholders = ",".join("?" * len(ids))
cursor.execute(f"SELECT * FROM habits WHERE id IN ({placeholders})", ids)

# NEVER do string formatting!
# BAD: cursor.execute(f"SELECT * FROM habits WHERE name = '{user_input}'")
```

### Row Factories

```python
# Return rows as dictionaries
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute("SELECT * FROM habits")
row = cursor.fetchone()
print(row["name"])  # Access by column name
print(row[0])       # Access by index
print(dict(row))    # Convert to dict
```

### Batch Operations

```python
# executemany for bulk inserts
data = [("Exercise",), ("Reading",), ("Meditation",)]
cursor.executemany("INSERT INTO habits (name) VALUES (?)", data)

# Wrap in transaction for performance
conn.execute("BEGIN")
try:
    for chunk in chunks(large_data, 1000):
        cursor.executemany("INSERT INTO habits (name) VALUES (?)", chunk)
    conn.commit()
except:
    conn.rollback()
    raise
```

---

## 10. Performance Tuning

### Essential PRAGMA Settings

```sql
-- Run on every connection
PRAGMA journal_mode = WAL;        -- Write-ahead logging (better concurrency)
PRAGMA synchronous = NORMAL;      -- Safe with WAL, faster than FULL
PRAGMA foreign_keys = ON;         -- Enable foreign key enforcement
PRAGMA cache_size = -64000;       -- 64MB page cache (negative = KB)
PRAGMA temp_store = MEMORY;       -- Store temp tables in RAM
PRAGMA mmap_size = 268435456;     -- 256MB memory-mapped I/O

-- Run periodically or before closing
PRAGMA optimize;                   -- Optimize query planner statistics
```

### PRAGMA Reference

| PRAGMA | Purpose | Recommended |
|--------|---------|-------------|
| `journal_mode` | Transaction journaling | `WAL` |
| `synchronous` | Disk sync frequency | `NORMAL` (with WAL) |
| `foreign_keys` | FK enforcement | `ON` |
| `cache_size` | Page cache size | `-64000` (64MB) |
| `temp_store` | Temp table location | `MEMORY` |
| `busy_timeout` | Lock wait time (ms) | `5000` |

### WAL Mode

```sql
PRAGMA journal_mode = WAL;
```

**Benefits**:
- Readers don't block writers
- Writers don't block readers
- Better crash recovery
- Faster for most workloads

**Limitations**:
- Doesn't work on network filesystems
- Creates `-wal` and `-shm` files alongside database

### Database Maintenance

```sql
-- Defragment and optimize (run during maintenance windows)
VACUUM;

-- Update statistics for query planner
ANALYZE;

-- Rebuild indexes
REINDEX;

-- Check database integrity
PRAGMA integrity_check;
```

---

## 11. Backup & Recovery

### Safe Backup Methods

```python
import sqlite3

def backup_database(source_path: str, dest_path: str):
    """Safe backup using SQLite's backup API."""
    source = sqlite3.connect(source_path)
    dest = sqlite3.connect(dest_path)

    with dest:
        source.backup(dest)

    dest.close()
    source.close()
```

```sql
-- VACUUM INTO creates a vacuumed copy (SQLite 3.27.0+)
VACUUM INTO '/path/to/backup.db';
```

### What NOT to Do

```bash
# NEVER use cp/copy on a live database - not transactionally safe!
cp database.db backup.db  # BAD!
```

### Litestream (Continuous Backup)

```yaml
# litestream.yml
dbs:
  - path: /data/habits.db
    replicas:
      - url: s3://bucket-name/habits
        sync-interval: 1s
```

### Integrity Checking

```sql
-- Full integrity check
PRAGMA integrity_check;

-- Quick check (faster)
PRAGMA quick_check;

-- Returns 'ok' if healthy
```

---

## 12. Anti-Patterns

### Configuration Mistakes

| Mistake | Solution |
|---------|----------|
| Not enabling foreign keys | `PRAGMA foreign_keys=ON` per connection |
| Using default journal mode | Enable WAL: `PRAGMA journal_mode=WAL` |
| SQLite on network filesystem | Use local filesystem only |

### Schema Mistakes

| Mistake | Solution |
|---------|----------|
| Storing comma-separated lists | Use proper junction tables |
| Not indexing foreign keys | Always index FK columns |
| Over-indexing | Only index frequently queried columns |
| Using wrong date format | Use ISO 8601: `YYYY-MM-DD` |

### Query Mistakes

| Mistake | Solution |
|---------|----------|
| `SELECT *` | Select only needed columns |
| LIKE for date queries | Use date comparisons |
| Functions on indexed columns | Create expression indexes |
| Not using EXPLAIN | Analyze slow queries |

### Python Mistakes

| Mistake | Solution |
|---------|----------|
| String formatting SQL | Use parameterized queries |
| Not closing connections | Use context managers |
| Creating engine per request | Create once, reuse |
| Ignoring N+1 queries | Use eager loading |

---

## Quick Reference

### Connection Setup Template

```python
from sqlalchemy import create_engine, event

engine = create_engine("sqlite:///habits.db", connect_args={"check_same_thread": False})

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA cache_size=-64000")
    cursor.execute("PRAGMA temp_store=MEMORY")
    cursor.close()
```

### SQLite Date Functions

```sql
-- Current date/time
SELECT date('now');                    -- 2025-01-15
SELECT datetime('now');                -- 2025-01-15 12:30:00
SELECT strftime('%s', 'now');          -- Unix timestamp

-- Date arithmetic
SELECT date('now', '-7 days');         -- 7 days ago
SELECT date('now', '+1 month');        -- 1 month from now
SELECT date('now', 'start of month');  -- First of current month

-- Extract parts
SELECT strftime('%Y', '2025-01-15');   -- 2025
SELECT strftime('%m', '2025-01-15');   -- 01
SELECT strftime('%d', '2025-01-15');   -- 15
```

---

## Resources

- [SQLite Documentation](https://sqlite.org/docs.html)
- [SQLite When to Use](https://sqlite.org/whentouse.html)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Litestream](https://litestream.io/)
