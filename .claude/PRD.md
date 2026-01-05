# Habit Tracker - Product Requirements Document

## 1. Executive Summary

Habit Tracker is a personal web application designed to help users build and maintain daily habits through simple tracking and streak-based motivation. The application provides a frictionless way to log daily habit completions, visualize progress over time, and stay motivated through streak tracking and completion rate metrics.

The core value proposition is simplicity: a local-first habit tracker without the complexity of account management, social features, or overwhelming customization options. Users can focus purely on building habits without distractions.

**MVP Goal:** Deliver a functional habit tracking application with daily completion logging, streak tracking, planned absence support, and calendar visualization—all running locally without authentication.

---

## 2. Mission

**Mission Statement:** Provide a simple, distraction-free tool for tracking daily habits and maintaining motivation through visible progress metrics.

### Core Principles

1. **Simplicity First** — Minimal features, maximum utility. Every feature must earn its place.
2. **Instant Feedback** — Completing a habit should feel immediate and satisfying.
3. **Motivation Over Guilt** — Show progress positively; completion rates alongside streaks prevent demoralization.
4. **Local & Private** — No accounts, no cloud, no data leaving the user's machine.
5. **Daily Focus** — Optimize for daily habits; avoid complexity of custom schedules.

---

## 3. Target Users

### Primary Persona: Self-Motivated Individual

- **Who:** A single user running the app locally for personal use
- **Technical Comfort:** Comfortable running local dev servers or simple executables
- **Goals:**
  - Build consistent daily habits (exercise, reading, meditation, etc.)
  - See visual proof of consistency to stay motivated
  - Simple tracking without overhead of complex apps
- **Pain Points:**
  - Existing habit trackers are bloated with features they don't need
  - Don't want to create accounts or share data
  - Streak-only tracking feels punishing when life happens

---

## 4. MVP Scope

### In Scope

**Core Functionality**
- ✅ Create, edit, and delete habits
- ✅ Archive habits (soft delete, preserves history)
- ✅ Mark habits as completed for a given day
- ✅ Mark days as "skipped" (planned absence, doesn't break streak)
- ✅ Undo completions/skips
- ✅ View all habits due today with completion status
- ✅ Current streak calculation per habit
- ✅ Longest streak tracking (personal best preserved)
- ✅ Completion rate percentage per habit
- ✅ Monthly calendar view showing completion history

**Technical**
- ✅ Python backend with FastAPI
- ✅ SQLite database for persistence
- ✅ React frontend with Vite
- ✅ Tailwind CSS for styling
- ✅ RESTful API design
- ✅ Local development setup (two terminal workflow)

### Out of Scope

**Deferred Features**
- ❌ Non-daily habits (weekly, specific days)
- ❌ Reminders/notifications
- ❌ Categories/tags for habits
- ❌ Grace period past midnight
- ❌ Streak freezes (planned absence covers this use case)
- ❌ Data export (CSV, JSON)
- ❌ Dark mode
- ❌ Mobile app (responsive web only)
- ❌ Multiple users/authentication
- ❌ Cloud sync
- ❌ Gamification (badges, points)

---

## 5. User Stories

### Primary User Stories

1. **As a user, I want to create a new habit, so that I can start tracking it daily.**
   - Example: Add "Morning meditation" with description "10 minutes of mindfulness"

2. **As a user, I want to mark a habit as complete with a single tap, so that tracking is frictionless.**
   - Example: Tap the checkbox next to "Exercise" and see immediate visual feedback

3. **As a user, I want to see all my habits for today on one screen, so that I know what I need to do.**
   - Example: Dashboard shows 5 habits with 3 completed, 2 remaining

4. **As a user, I want to see my current streak for each habit, so that I stay motivated to maintain it.**
   - Example: "Reading: 14 day streak" displayed prominently

5. **As a user, I want to mark a day as "skipped" for planned absences, so that vacations don't break my streak.**
   - Example: Mark "Exercise" as skipped for travel days; streak continues when I return

6. **As a user, I want to see my completion rate alongside my streak, so that one bad day doesn't feel like failure.**
   - Example: "Exercise: 5 day streak | 87% completion rate"

7. **As a user, I want to view a calendar of my habit history, so that I can see patterns over time.**
   - Example: Monthly grid with green (completed), gray (skipped), red (missed) indicators

8. **As a user, I want to archive old habits without losing their history, so that I can focus on current goals.**
   - Example: Archive "Learn Spanish" but still see its historical data if needed

---

## 6. Core Architecture & Patterns

### High-Level Architecture

```
┌─────────────────┐     HTTP/JSON      ┌─────────────────┐
│                 │ ◄───────────────► │                 │
│  React + Vite   │                    │    FastAPI      │
│   (Frontend)    │                    │   (Backend)     │
│   Port 5173     │                    │   Port 8000     │
└─────────────────┘                    └────────┬────────┘
                                                │
                                                ▼
                                       ┌─────────────────┐
                                       │     SQLite      │
                                       │   (Database)    │
                                       └─────────────────┘
```

### Directory Structure

```
habit-tracker/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── database.py          # SQLite connection & session
│   │   ├── models.py            # SQLAlchemy ORM models
│   │   ├── schemas.py           # Pydantic request/response schemas
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── habits.py        # Habit CRUD endpoints
│   │       └── completions.py   # Completion/skip endpoints
│   ├── habits.db                # SQLite database file
│   ├── pyproject.toml           # Python dependencies
│   └── requirements.txt         # Pinned dependencies (optional)
│
├── frontend/
│   ├── src/
│   │   ├── components/          # Reusable UI components
│   │   │   ├── HabitCard.jsx
│   │   │   ├── HabitForm.jsx
│   │   │   ├── Calendar.jsx
│   │   │   └── StreakBadge.jsx
│   │   ├── pages/               # Route-level components
│   │   │   ├── Dashboard.jsx
│   │   │   └── HabitDetail.jsx
│   │   ├── api/                 # API client functions
│   │   │   └── habits.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css            # Tailwind imports
│   ├── public/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
├── .gitignore
├── .claude/
│   └── PRD.md                   # This document
└── README.md
```

### Key Design Patterns

- **Repository Pattern** — Database operations abstracted in models/routers
- **Pydantic Schemas** — Request validation and response serialization
- **Component Composition** — React components are small and composable
- **API Client Layer** — Frontend API calls centralized in `api/` directory
- **Optimistic UI** — Update UI immediately, sync with server in background

---

## 7. Features

### 7.1 Habit Management

**Purpose:** Create, update, and manage habits

**Operations:**
- Create habit with name and optional description
- Edit habit name/description
- Archive habit (removes from today view, preserves history)
- Delete habit permanently (with confirmation)

**Key Features:**
- Habit name required, description optional
- Optional color picker for visual distinction
- Archived habits hidden from main view but accessible

### 7.2 Daily Completion Tracking

**Purpose:** Log daily habit completions

**Operations:**
- Mark habit as completed for today
- Mark habit as skipped (planned absence)
- Undo completion or skip
- View completion status for any past date

**Key Features:**
- Single-tap completion with instant visual feedback
- Three states: completed (green), skipped (gray), incomplete (default)
- Can modify today and past dates (for catching up)
- Completions are date-based (one per habit per day)

### 7.3 Streak Tracking

**Purpose:** Motivate consistency through streak visibility

**Calculations:**
- **Current Streak:** Consecutive days completed (skipped days don't break streak)
- **Longest Streak:** Personal best, preserved even after streak breaks
- **Completion Rate:** (completed days / total days since habit created) × 100

**Key Features:**
- Streaks displayed prominently on habit cards
- Completion rate shown alongside streak to reduce pressure
- Longest streak celebrated when achieved

### 7.4 Calendar View

**Purpose:** Visualize habit history over time

**Features:**
- Monthly grid layout
- Color-coded days: green (completed), gray (skipped), red (missed), default (future/not due)
- Navigate between months
- Tap day to view/edit completion status
- Today's date highlighted

---

## 8. Technology Stack

### Backend

| Component | Technology | Version |
|-----------|------------|---------|
| Framework | FastAPI | ^0.100.0 |
| Server | Uvicorn | ^0.23.0 |
| ORM | SQLAlchemy | ^2.0.0 |
| Validation | Pydantic | ^2.0.0 |
| Database | SQLite | 3.x (built-in) |

### Frontend

| Component | Technology | Version |
|-----------|------------|---------|
| Framework | React | ^18.x |
| Build Tool | Vite | ^5.x |
| Routing | react-router-dom | ^6.x |
| Server State | TanStack Query | ^5.x |
| Styling | Tailwind CSS | ^3.x |
| Date Utilities | date-fns | ^3.x |
| Icons | lucide-react | ^0.300.0 |

### Development Tools

| Tool | Purpose |
|------|---------|
| Python venv | Virtual environment |
| npm/pnpm | Package management |
| Ruff | Python linting/formatting |
| ESLint | JavaScript linting |

---

## 9. Security & Configuration

### Security Scope

**In Scope:**
- ✅ Input validation on all API endpoints (Pydantic)
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ CORS configuration for local development

**Out of Scope:**
- ❌ Authentication/authorization (single local user)
- ❌ HTTPS (local development only)
- ❌ Rate limiting
- ❌ CSRF protection

### Configuration

**Backend (environment variables):**
```
DATABASE_URL=sqlite:///./habits.db
CORS_ORIGINS=http://localhost:5173
```

**Frontend (vite.config.js):**
```javascript
server: {
  proxy: {
    '/api': 'http://localhost:8000'
  }
}
```

### Deployment

MVP runs locally via development servers:
- Backend: `uvicorn app.main:app --reload`
- Frontend: `npm run dev`

---

## 10. API Specification

### Base URL
```
http://localhost:8000/api
```

### Endpoints

#### Habits

**GET /api/habits**
List all habits with calculated stats.

Response:
```json
{
  "habits": [
    {
      "id": 1,
      "name": "Exercise",
      "description": "30 minutes of activity",
      "color": "#10B981",
      "currentStreak": 5,
      "longestStreak": 14,
      "completionRate": 0.87,
      "completedToday": true,
      "createdAt": "2025-01-01T00:00:00Z",
      "archivedAt": null
    }
  ]
}
```

**POST /api/habits**
Create a new habit.

Request:
```json
{
  "name": "Read",
  "description": "Read for 20 minutes",
  "color": "#3B82F6"
}
```

**PUT /api/habits/{id}**
Update a habit.

**DELETE /api/habits/{id}**
Permanently delete a habit.

**PATCH /api/habits/{id}/archive**
Archive a habit.

#### Completions

**POST /api/habits/{id}/complete**
Mark habit as completed for a date.

Request:
```json
{
  "date": "2025-01-04",
  "notes": "Ran 5k today"
}
```

**POST /api/habits/{id}/skip**
Mark habit as skipped for a date.

Request:
```json
{
  "date": "2025-01-04",
  "reason": "Traveling"
}
```

**DELETE /api/habits/{id}/completions/{date}**
Remove a completion or skip entry.

**GET /api/habits/{id}/completions**
Get completion history for a habit.

Query params: `?start=2025-01-01&end=2025-01-31`

Response:
```json
{
  "completions": [
    {
      "date": "2025-01-01",
      "status": "completed",
      "notes": null
    },
    {
      "date": "2025-01-02",
      "status": "skipped",
      "notes": "Sick day"
    }
  ]
}
```

---

## 11. Success Criteria

### MVP Success Definition

The MVP is successful when a user can:
1. Add a new habit and see it on their dashboard
2. Complete the habit daily and watch their streak grow
3. Skip a day for planned absence without losing their streak
4. View their completion history on a calendar
5. Feel motivated by visible progress metrics

### Functional Requirements

- ✅ Create, edit, delete, and archive habits
- ✅ Mark habits complete or skipped with single interaction
- ✅ Calculate and display current streak accurately
- ✅ Preserve longest streak after streak breaks
- ✅ Display completion rate as percentage
- ✅ Render monthly calendar with completion history
- ✅ Persist all data across browser sessions (SQLite)
- ✅ Handle date boundaries correctly (local time)

### Quality Indicators

- Page load under 1 second
- Completion action feedback under 100ms
- No data loss on normal usage
- Works in Chrome, Firefox, Safari
- Responsive layout (desktop + mobile browsers)

---

## 12. Implementation Phases

### Phase 1: Backend Foundation

**Goal:** Functional API with database persistence

**Deliverables:**
- ✅ Project structure and Python virtual environment
- ✅ SQLite database with habits and completions tables
- ✅ CRUD endpoints for habits
- ✅ Completion/skip endpoints
- ✅ Streak calculation logic
- ✅ API tested via Swagger UI

**Validation:** Can create habits and log completions via API docs

---

### Phase 2: Frontend Foundation

**Goal:** Basic React app displaying habits

**Deliverables:**
- ✅ Vite + React project scaffolded
- ✅ Tailwind CSS configured
- ✅ API client with TanStack Query
- ✅ Dashboard page with habit list
- ✅ Habit creation form
- ✅ Completion toggle functionality

**Validation:** Can add habits and mark them complete in browser

---

### Phase 3: Core Features

**Goal:** Full MVP functionality

**Deliverables:**
- ✅ Streak and completion rate display
- ✅ Skip functionality for planned absences
- ✅ Edit and archive habit flows
- ✅ Calendar view component
- ✅ Habit detail page with history

**Validation:** All user stories achievable

---

### Phase 4: Polish

**Goal:** Production-ready MVP

**Deliverables:**
- ✅ Loading and error states
- ✅ Empty states (no habits yet)
- ✅ Confirmation dialogs for destructive actions
- ✅ Mobile-responsive layout
- ✅ README with setup instructions

**Validation:** Smooth user experience, no rough edges

---

## 13. Future Considerations

### Post-MVP Enhancements

- **Non-daily habits** — Weekly or specific-day schedules
- **Data export** — CSV/JSON export of all data
- **Dark mode** — System preference detection
- **Reminders** — Browser notifications (with permission)
- **Grace period** — 2-4 hours past midnight to complete
- **Habit templates** — Pre-defined habits to choose from
- **Weekly/monthly reports** — Summary of progress

### Technical Improvements

- **Single executable** — Package as standalone app (PyInstaller + embedded frontend)
- **Desktop app** — Electron or Tauri wrapper
- **PWA support** — Installable web app with offline capability
- **Database migrations** — Alembic for schema evolution

---

## 14. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Streak calculation bugs** | Users lose trust if streaks are wrong | Comprehensive unit tests for streak logic; manual testing with edge cases |
| **Data loss** | Complete failure of app value | SQLite is robust; document backup procedures; future: export feature |
| **Date/timezone issues** | Completions recorded on wrong day | Use consistent date handling (date-fns); test across timezones |
| **Scope creep** | MVP never ships | Strict adherence to MVP scope; defer features explicitly |
| **Poor mobile UX** | App unusable on primary device | Mobile-first design; test on real devices early |

---

## 15. Appendix

### Database Schema

```sql
CREATE TABLE habits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    color TEXT DEFAULT '#10B981',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    archived_at TIMESTAMP
);

CREATE TABLE completions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id INTEGER NOT NULL,
    completed_date TEXT NOT NULL,  -- YYYY-MM-DD format
    status TEXT NOT NULL DEFAULT 'completed',  -- 'completed' or 'skipped'
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE,
    UNIQUE(habit_id, completed_date)
);

CREATE INDEX idx_completions_habit_date ON completions(habit_id, completed_date);
```

### Key Dependencies

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/)
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)
- [TanStack Query Documentation](https://tanstack.com/query/latest)
- [date-fns Documentation](https://date-fns.org/)
