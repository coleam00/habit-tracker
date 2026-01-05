from sqlalchemy import CheckConstraint, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Habit(Base):
    """Habit model representing a trackable daily habit."""

    __tablename__ = "habits"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500))
    color: Mapped[str] = mapped_column(String(7), default="#10B981")
    created_at: Mapped[str] = mapped_column(String(19), nullable=False)  # ISO datetime
    archived_at: Mapped[str | None] = mapped_column(String(19))  # ISO datetime

    completions: Mapped[list["Completion"]] = relationship(
        back_populates="habit",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (CheckConstraint("length(name) > 0", name="name_not_empty"),)


class Completion(Base):
    """Completion model representing a habit completion or skip for a specific date."""

    __tablename__ = "completions"

    id: Mapped[int] = mapped_column(primary_key=True)
    habit_id: Mapped[int] = mapped_column(
        ForeignKey("habits.id", ondelete="CASCADE"),
        nullable=False,
    )
    completed_date: Mapped[str] = mapped_column(String(10), nullable=False)  # YYYY-MM-DD
    status: Mapped[str] = mapped_column(String(10), default="completed")  # completed, skipped
    notes: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[str] = mapped_column(String(19), nullable=False)  # ISO datetime

    habit: Mapped["Habit"] = relationship(back_populates="completions")

    __table_args__ = (
        UniqueConstraint("habit_id", "completed_date", name="uq_habit_date"),
        CheckConstraint("status IN ('completed', 'skipped')", name="valid_status"),
        Index("idx_completions_habit_date", "habit_id", "completed_date"),
    )
