from datetime import date, datetime, timedelta
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Completion, Habit
from app.schemas import (
    HabitCreate,
    HabitListResponse,
    HabitResponse,
    HabitUpdate,
)

logger = structlog.get_logger()

router = APIRouter(prefix="/habits", tags=["habits"])


def _prev_day(d: date) -> date:
    """Get the previous day."""
    return d - timedelta(days=1)


def calculate_streak(completions: list[Completion], today: date) -> int:
    """Calculate current streak from completions.

    Streak counts consecutive completed days from today backwards.
    Skipped days don't break the streak.
    """
    if not completions:
        return 0

    # Build map of date to status
    completion_map = {c.completed_date: c.status for c in completions}

    streak = 0
    check_date = today

    while True:
        date_str = check_date.isoformat()

        if date_str in completion_map:
            if completion_map[date_str] == "completed":
                streak += 1
            # Skipped days don't break streak, just continue
            check_date = _prev_day(check_date)
        else:
            # No entry for this date - streak breaks
            # But only if we've started counting (found at least one completion)
            if streak > 0:
                break
            # If no completion today, check yesterday
            check_date = _prev_day(check_date)
            # If we've gone back more than 1 day without finding anything, no streak
            if (today - check_date).days > 1:
                break

    return streak


def calculate_longest_streak(completions: list[Completion]) -> int:
    """Calculate the longest streak ever achieved."""
    if not completions:
        return 0

    # Get all completed dates sorted
    completed_dates = sorted(
        [date.fromisoformat(c.completed_date) for c in completions if c.status == "completed"]
    )

    if not completed_dates:
        return 0

    # Build map of skipped dates for gap handling
    skipped_dates = {c.completed_date for c in completions if c.status == "skipped"}

    longest = 1
    current = 1

    for i in range(1, len(completed_dates)):
        prev = completed_dates[i - 1]
        curr = completed_dates[i]
        gap = (curr - prev).days

        if gap == 1:
            # Consecutive day
            current += 1
        elif gap > 1:
            # Check if all gap days are skipped
            all_skipped = True
            check = prev
            while check < curr:
                check = check + timedelta(days=1)
                if check < curr and check.isoformat() not in skipped_dates:
                    all_skipped = False
                    break

            if all_skipped:
                current += 1
            else:
                current = 1

        longest = max(longest, current)

    return longest


def calculate_completion_rate(habit: Habit, completions: list[Completion], today: date) -> float:
    """Calculate completion rate as percentage."""
    created = date.fromisoformat(habit.created_at[:10])
    total_days = (today - created).days + 1

    if total_days <= 0:
        return 0.0

    # Only count completions on or after the habit was created
    completed_count = sum(
        1 for c in completions
        if c.status == "completed" and date.fromisoformat(c.completed_date) >= created
    )
    return round((completed_count / total_days) * 100, 1)


def is_completed_today(completions: list[Completion], today: date) -> bool:
    """Check if habit is completed today."""
    today_str = today.isoformat()
    return any(c.completed_date == today_str and c.status == "completed" for c in completions)


def build_habit_response(habit: Habit, today: date | None = None) -> HabitResponse:
    """Build a HabitResponse with calculated stats."""
    if today is None:
        today = date.today()

    completions = habit.completions

    return HabitResponse(
        id=habit.id,
        name=habit.name,
        description=habit.description,
        color=habit.color,
        current_streak=calculate_streak(completions, today),
        longest_streak=calculate_longest_streak(completions),
        completion_rate=calculate_completion_rate(habit, completions, today),
        completed_today=is_completed_today(completions, today),
        created_at=habit.created_at,
        archived_at=habit.archived_at,
    )


@router.get("/", response_model=HabitListResponse)
def list_habits(
    db: Annotated[Session, Depends(get_db)],
    include_archived: bool = False,
) -> HabitListResponse:
    """List all habits with calculated stats."""
    query = select(Habit)
    if not include_archived:
        query = query.where(Habit.archived_at.is_(None))

    habits = db.execute(query).scalars().all()
    today = date.today()

    return HabitListResponse(habits=[build_habit_response(h, today) for h in habits])


@router.post("/", response_model=HabitResponse, status_code=status.HTTP_201_CREATED)
def create_habit(
    habit_data: HabitCreate,
    db: Annotated[Session, Depends(get_db)],
) -> HabitResponse:
    """Create a new habit."""
    habit = Habit(
        name=habit_data.name,
        description=habit_data.description,
        color=habit_data.color,
        created_at=datetime.now().isoformat(timespec="seconds"),
    )
    db.add(habit)
    db.commit()
    db.refresh(habit)

    logger.info("Habit created", habit_id=habit.id, habit_name=habit.name)

    return build_habit_response(habit)


@router.get("/{habit_id}", response_model=HabitResponse)
def get_habit(
    habit_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> HabitResponse:
    """Get a specific habit by ID."""
    habit = db.get(Habit, habit_id)
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found",
        )

    return build_habit_response(habit)


@router.put("/{habit_id}", response_model=HabitResponse)
def update_habit(
    habit_id: int,
    habit_data: HabitUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> HabitResponse:
    """Update an existing habit."""
    habit = db.get(Habit, habit_id)
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found",
        )

    update_data = habit_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(habit, field, value)

    db.commit()
    db.refresh(habit)

    logger.info("Habit updated", habit_id=habit.id)

    return build_habit_response(habit)


@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_habit(
    habit_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    """Permanently delete a habit."""
    habit = db.get(Habit, habit_id)
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found",
        )

    db.delete(habit)
    db.commit()

    logger.info("Habit deleted", habit_id=habit_id)


@router.patch("/{habit_id}/archive", response_model=HabitResponse)
def archive_habit(
    habit_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> HabitResponse:
    """Archive a habit (soft delete)."""
    habit = db.get(Habit, habit_id)
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found",
        )

    habit.archived_at = datetime.now().isoformat(timespec="seconds")
    db.commit()
    db.refresh(habit)

    logger.info("Habit archived", habit_id=habit.id)

    return build_habit_response(habit)
