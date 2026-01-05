class AppException(Exception):
    """Base exception for application errors."""

    def __init__(self, status_code: int, detail: str, error_code: str):
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code
        super().__init__(detail)


class HabitNotFoundError(AppException):
    """Raised when a habit is not found."""

    def __init__(self, habit_id: int):
        super().__init__(
            status_code=404,
            detail=f"Habit with ID {habit_id} not found",
            error_code="HABIT_NOT_FOUND",
        )


class CompletionNotFoundError(AppException):
    """Raised when a completion is not found."""

    def __init__(self, habit_id: int, date: str):
        super().__init__(
            status_code=404,
            detail=f"No completion found for habit {habit_id} on {date}",
            error_code="COMPLETION_NOT_FOUND",
        )


class DuplicateCompletionError(AppException):
    """Raised when trying to create a duplicate completion."""

    def __init__(self, habit_id: int, date: str):
        super().__init__(
            status_code=409,
            detail=f"Completion already exists for habit {habit_id} on {date}",
            error_code="DUPLICATE_COMPLETION",
        )
