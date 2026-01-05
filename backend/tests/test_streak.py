from dataclasses import dataclass
from datetime import date, timedelta

from app.routers.habits import calculate_longest_streak, calculate_streak


@dataclass
class MockCompletion:
    """Mock completion object for unit testing streak calculations."""

    completed_date: str
    status: str = "completed"


class TestStreakCalculation:
    """Unit tests for streak calculation logic."""

    def _make_completion(self, date_str: str, status: str = "completed") -> MockCompletion:
        """Helper to create a mock completion."""
        return MockCompletion(completed_date=date_str, status=status)

    def test_empty_completions_returns_zero(self):
        """No completions means no streak."""
        assert calculate_streak([], date.today()) == 0

    def test_single_completion_today(self):
        """Single completion today is streak of 1."""
        today = date.today()
        completions = [self._make_completion(today.isoformat())]

        assert calculate_streak(completions, today) == 1

    def test_single_completion_yesterday(self):
        """Single completion yesterday is streak of 1."""
        today = date.today()
        yesterday = today - timedelta(days=1)
        completions = [self._make_completion(yesterday.isoformat())]

        assert calculate_streak(completions, today) == 1

    def test_consecutive_days(self):
        """Consecutive completions count as streak."""
        today = date.today()
        completions = [
            self._make_completion((today - timedelta(days=i)).isoformat()) for i in range(5)
        ]

        assert calculate_streak(completions, today) == 5

    def test_gap_breaks_streak(self):
        """Missing day breaks the streak."""
        today = date.today()
        completions = [
            self._make_completion(today.isoformat()),
            self._make_completion((today - timedelta(days=2)).isoformat()),  # Gap
        ]

        assert calculate_streak(completions, today) == 1

    def test_skipped_day_doesnt_break_streak(self):
        """Skipped days don't break the streak."""
        today = date.today()
        completions = [
            self._make_completion(today.isoformat(), "completed"),
            self._make_completion((today - timedelta(days=1)).isoformat(), "skipped"),
            self._make_completion((today - timedelta(days=2)).isoformat(), "completed"),
        ]

        assert calculate_streak(completions, today) == 2

    def test_old_completion_no_streak(self):
        """Old completion with no recent activity means no current streak."""
        today = date.today()
        old_date = today - timedelta(days=30)
        completions = [self._make_completion(old_date.isoformat())]

        assert calculate_streak(completions, today) == 0


class TestLongestStreak:
    """Unit tests for longest streak calculation."""

    def _make_completion(self, date_str: str, status: str = "completed") -> MockCompletion:
        """Helper to create a mock completion."""
        return MockCompletion(completed_date=date_str, status=status)

    def test_empty_completions_returns_zero(self):
        """No completions means no longest streak."""
        assert calculate_longest_streak([]) == 0

    def test_single_completion(self):
        """Single completion is longest streak of 1."""
        completions = [self._make_completion("2025-01-01")]

        assert calculate_longest_streak(completions) == 1

    def test_consecutive_days(self):
        """Consecutive days counted correctly."""
        completions = [
            self._make_completion("2025-01-01"),
            self._make_completion("2025-01-02"),
            self._make_completion("2025-01-03"),
        ]

        assert calculate_longest_streak(completions) == 3

    def test_multiple_streaks_returns_longest(self):
        """Returns the longest of multiple streaks."""
        completions = [
            # First streak: 2 days
            self._make_completion("2025-01-01"),
            self._make_completion("2025-01-02"),
            # Gap
            # Second streak: 4 days
            self._make_completion("2025-01-10"),
            self._make_completion("2025-01-11"),
            self._make_completion("2025-01-12"),
            self._make_completion("2025-01-13"),
        ]

        assert calculate_longest_streak(completions) == 4

    def test_skipped_only_not_counted(self):
        """Only skipped days don't contribute to streak count."""
        completions = [
            self._make_completion("2025-01-01", "skipped"),
            self._make_completion("2025-01-02", "skipped"),
        ]

        assert calculate_longest_streak(completions) == 0


class TestCompletionRate:
    """Unit tests for completion rate calculation."""

    def test_completion_rate_never_exceeds_100_percent(self):
        """BUG FIX: Completion rate should never exceed 100% with pre-creation dates."""
        from datetime import date, timedelta

        from app.routers.habits import calculate_completion_rate

        # Mock habit created today
        class MockHabit:
            created_at = date.today().isoformat() + "T00:00:00"

        class MockCompletion:
            def __init__(self, date_str, status="completed"):
                self.completed_date = date_str
                self.status = status

        habit = MockHabit()
        today = date.today()

        # 5 completions including pre-creation dates
        completions = [
            MockCompletion((today - timedelta(days=i)).isoformat())
            for i in range(5)
        ]

        rate = calculate_completion_rate(habit, completions, today)
        assert rate == 100.0
        assert rate <= 100.0

    def test_completion_rate_ignores_pre_creation_completions(self):
        """Only completions on/after creation date should count."""
        from datetime import date

        from app.routers.habits import calculate_completion_rate

        class MockHabit:
            created_at = "2025-01-03T00:00:00"  # Created Jan 3

        class MockCompletion:
            def __init__(self, date_str, status="completed"):
                self.completed_date = date_str
                self.status = status

        habit = MockHabit()
        today = date(2025, 1, 5)  # Today is Jan 5 (3 days since creation)

        completions = [
            MockCompletion("2025-01-01"),  # Before creation - should be ignored
            MockCompletion("2025-01-02"),  # Before creation - should be ignored
            MockCompletion("2025-01-03"),  # On creation - counts
            MockCompletion("2025-01-04"),  # After creation - counts
            MockCompletion("2025-01-05"),  # Today - counts
        ]

        rate = calculate_completion_rate(habit, completions, today)
        assert rate == 100.0  # 3 valid completions in 3 days

    def test_completion_rate_partial_completion(self):
        """Completion rate calculated correctly with partial completions."""
        from datetime import date

        from app.routers.habits import calculate_completion_rate

        class MockHabit:
            created_at = "2025-01-01T00:00:00"  # Created Jan 1

        class MockCompletion:
            def __init__(self, date_str, status="completed"):
                self.completed_date = date_str
                self.status = status

        habit = MockHabit()
        today = date(2025, 1, 10)  # Today is Jan 10 (10 days since creation)

        completions = [
            MockCompletion("2025-01-01"),
            MockCompletion("2025-01-02"),
            MockCompletion("2025-01-03"),
            MockCompletion("2025-01-04"),
            MockCompletion("2025-01-05"),
        ]

        rate = calculate_completion_rate(habit, completions, today)
        assert rate == 50.0  # 5 completions in 10 days
