from datetime import date

import pytest
from fastapi.testclient import TestClient


class TestCompletionsAPI:
    """Integration tests for the completions API."""

    @pytest.fixture
    def habit_id(self, client: TestClient) -> int:
        """Create a habit and return its ID."""
        response = client.post("/api/habits", json={"name": "Test Habit"})
        return response.json()["id"]

    def test_complete_habit_returns_201(self, client: TestClient, habit_id: int):
        """Test completing a habit."""
        response = client.post(
            f"/api/habits/{habit_id}/complete",
            json={"date": "2025-01-04"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["date"] == "2025-01-04"
        assert data["status"] == "completed"

    def test_complete_habit_with_notes(self, client: TestClient, habit_id: int):
        """Test completing with notes."""
        response = client.post(
            f"/api/habits/{habit_id}/complete",
            json={"date": "2025-01-04", "notes": "Ran 5k"},
        )

        assert response.status_code == 201
        assert response.json()["notes"] == "Ran 5k"

    def test_complete_duplicate_returns_409(self, client: TestClient, habit_id: int):
        """Test conflict on duplicate completion."""
        client.post(
            f"/api/habits/{habit_id}/complete",
            json={"date": "2025-01-04"},
        )

        response = client.post(
            f"/api/habits/{habit_id}/complete",
            json={"date": "2025-01-04"},
        )

        assert response.status_code == 409

    def test_complete_nonexistent_habit_returns_404(self, client: TestClient):
        """Test 404 for non-existent habit."""
        response = client.post(
            "/api/habits/99999/complete",
            json={"date": "2025-01-04"},
        )

        assert response.status_code == 404

    def test_complete_invalid_date_returns_422(self, client: TestClient, habit_id: int):
        """Test validation for invalid date format."""
        response = client.post(
            f"/api/habits/{habit_id}/complete",
            json={"date": "01-04-2025"},  # Wrong format
        )

        assert response.status_code == 422

    def test_skip_habit_returns_201(self, client: TestClient, habit_id: int):
        """Test skipping a habit."""
        response = client.post(
            f"/api/habits/{habit_id}/skip",
            json={"date": "2025-01-04", "reason": "Traveling"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["date"] == "2025-01-04"
        assert data["status"] == "skipped"
        assert data["notes"] == "Traveling"

    def test_delete_completion(self, client: TestClient, habit_id: int):
        """Test removing a completion (undo)."""
        client.post(
            f"/api/habits/{habit_id}/complete",
            json={"date": "2025-01-04"},
        )

        response = client.delete(f"/api/habits/{habit_id}/completions/2025-01-04")

        assert response.status_code == 204

    def test_delete_nonexistent_completion_returns_404(
        self, client: TestClient, habit_id: int
    ):
        """Test 404 for non-existent completion."""
        response = client.delete(f"/api/habits/{habit_id}/completions/2025-01-04")

        assert response.status_code == 404

    def test_get_completions(self, client: TestClient, habit_id: int):
        """Test getting completion history."""
        client.post(f"/api/habits/{habit_id}/complete", json={"date": "2025-01-01"})
        client.post(f"/api/habits/{habit_id}/complete", json={"date": "2025-01-02"})
        client.post(f"/api/habits/{habit_id}/skip", json={"date": "2025-01-03"})

        response = client.get(f"/api/habits/{habit_id}/completions")

        assert response.status_code == 200
        completions = response.json()["completions"]
        assert len(completions) == 3

    def test_get_completions_filtered_by_date(self, client: TestClient, habit_id: int):
        """Test filtering completions by date range."""
        client.post(f"/api/habits/{habit_id}/complete", json={"date": "2025-01-01"})
        client.post(f"/api/habits/{habit_id}/complete", json={"date": "2025-01-15"})
        client.post(f"/api/habits/{habit_id}/complete", json={"date": "2025-02-01"})

        response = client.get(
            f"/api/habits/{habit_id}/completions",
            params={"start": "2025-01-01", "end": "2025-01-31"},
        )

        assert response.status_code == 200
        completions = response.json()["completions"]
        assert len(completions) == 2

    def test_habit_shows_completed_today(self, client: TestClient, habit_id: int):
        """Test that completing today updates the habit response."""
        today = date.today().isoformat()

        # Before completion
        habit = client.get(f"/api/habits/{habit_id}").json()
        assert habit["completed_today"] is False

        # Complete today
        client.post(f"/api/habits/{habit_id}/complete", json={"date": today})

        # After completion
        habit = client.get(f"/api/habits/{habit_id}").json()
        assert habit["completed_today"] is True
