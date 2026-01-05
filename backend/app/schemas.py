from pydantic import BaseModel, ConfigDict, Field, field_validator

# --- Habit Schemas ---


class HabitBase(BaseModel):
    """Base schema with shared habit fields."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)


class HabitCreate(HabitBase):
    """Schema for creating a new habit."""

    color: str = Field(default="#10B981", pattern=r"^#[0-9A-Fa-f]{6}$")

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be blank")
        return v.strip()


class HabitUpdate(BaseModel):
    """Schema for updating an existing habit. All fields optional."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("Name cannot be blank")
        return v.strip() if v else v


class HabitResponse(HabitBase):
    """Schema for habit responses including computed stats."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    color: str
    current_streak: int = 0
    longest_streak: int = 0
    completion_rate: float = 0.0
    completed_today: bool = False
    created_at: str
    archived_at: str | None = None


class HabitListResponse(BaseModel):
    """Schema for listing habits."""

    habits: list[HabitResponse]


# --- Completion Schemas ---


class CompletionBase(BaseModel):
    """Base schema for completion data."""

    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    notes: str | None = Field(None, max_length=500)


class CompletionCreate(CompletionBase):
    """Schema for creating a completion."""

    pass


class SkipCreate(CompletionBase):
    """Schema for marking a day as skipped."""

    reason: str | None = Field(None, max_length=500)


class CompletionResponse(BaseModel):
    """Schema for completion responses."""

    model_config = ConfigDict(from_attributes=True)

    date: str
    status: str
    notes: str | None = None


class CompletionListResponse(BaseModel):
    """Schema for listing completions."""

    completions: list[CompletionResponse]
