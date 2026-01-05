from datetime import datetime
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Completion, Habit
from app.schemas import (
    CompletionCreate,
    CompletionListResponse,
    CompletionResponse,
    SkipCreate,
)

logger = structlog.get_logger()

router = APIRouter(prefix="/habits/{habit_id}", tags=["completions"])


def get_habit_or_404(habit_id: int, db: Session) -> Habit:
    """Get habit by ID or raise 404."""
    habit = db.get(Habit, habit_id)
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found",
        )
    return habit


@router.post("/complete", response_model=CompletionResponse, status_code=status.HTTP_201_CREATED)
def complete_habit(
    habit_id: int,
    completion_data: CompletionCreate,
    db: Annotated[Session, Depends(get_db)],
) -> CompletionResponse:
    """Mark a habit as completed for a specific date."""
    habit = get_habit_or_404(habit_id, db)

    completion = Completion(
        habit_id=habit.id,
        completed_date=completion_data.date,
        status="completed",
        notes=completion_data.notes,
        created_at=datetime.now().isoformat(timespec="seconds"),
    )

    try:
        db.add(completion)
        db.commit()
        db.refresh(completion)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Completion already exists for habit {habit_id} on {completion_data.date}",
        )

    logger.info(
        "Habit completed",
        habit_id=habit_id,
        date=completion_data.date,
    )

    return CompletionResponse(
        date=completion.completed_date,
        status=completion.status,
        notes=completion.notes,
    )


@router.post("/skip", response_model=CompletionResponse, status_code=status.HTTP_201_CREATED)
def skip_habit(
    habit_id: int,
    skip_data: SkipCreate,
    db: Annotated[Session, Depends(get_db)],
) -> CompletionResponse:
    """Mark a habit as skipped for a specific date (planned absence)."""
    habit = get_habit_or_404(habit_id, db)

    completion = Completion(
        habit_id=habit.id,
        completed_date=skip_data.date,
        status="skipped",
        notes=skip_data.reason,
        created_at=datetime.now().isoformat(timespec="seconds"),
    )

    try:
        db.add(completion)
        db.commit()
        db.refresh(completion)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Entry already exists for habit {habit_id} on {skip_data.date}",
        )

    logger.info(
        "Habit skipped",
        habit_id=habit_id,
        date=skip_data.date,
    )

    return CompletionResponse(
        date=completion.completed_date,
        status=completion.status,
        notes=completion.notes,
    )


@router.delete("/completions/{date}", status_code=status.HTTP_204_NO_CONTENT)
def delete_completion(
    habit_id: int,
    date: str,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    """Remove a completion or skip entry (undo)."""
    habit = get_habit_or_404(habit_id, db)

    completion = db.execute(
        select(Completion).where(
            Completion.habit_id == habit.id,
            Completion.completed_date == date,
        )
    ).scalar_one_or_none()

    if not completion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No completion found for habit {habit_id} on {date}",
        )

    db.delete(completion)
    db.commit()

    logger.info(
        "Completion removed",
        habit_id=habit_id,
        date=date,
    )


@router.get("/completions", response_model=CompletionListResponse)
def get_completions(
    habit_id: int,
    db: Annotated[Session, Depends(get_db)],
    start: Annotated[str | None, Query(pattern=r"^\d{4}-\d{2}-\d{2}$")] = None,
    end: Annotated[str | None, Query(pattern=r"^\d{4}-\d{2}-\d{2}$")] = None,
) -> CompletionListResponse:
    """Get completion history for a habit with optional date filtering."""
    habit = get_habit_or_404(habit_id, db)

    query = select(Completion).where(Completion.habit_id == habit.id)

    if start:
        query = query.where(Completion.completed_date >= start)
    if end:
        query = query.where(Completion.completed_date <= end)

    query = query.order_by(Completion.completed_date.desc())

    completions = db.execute(query).scalars().all()

    return CompletionListResponse(
        completions=[
            CompletionResponse(
                date=c.completed_date,
                status=c.status,
                notes=c.notes,
            )
            for c in completions
        ]
    )
