from fastapi.testclient import TestClient


class TestHabitsAPI:
    """Integration tests for the habits API."""

    def test_create_habit_returns_201(self, client: TestClient):
        """Test creating a new habit."""
        response = client.post(
            "/api/habits",
            json={"name": "Exercise", "description": "Daily workout"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Exercise"
        assert data["description"] == "Daily workout"
        assert data["color"] == "#10B981"
        assert data["current_streak"] == 0
        assert data["completed_today"] is False
        assert "id" in data
        assert "created_at" in data

    def test_create_habit_with_custom_color(self, client: TestClient):
        """Test creating a habit with custom color."""
        response = client.post(
            "/api/habits",
            json={"name": "Reading", "color": "#3B82F6"},
        )

        assert response.status_code == 201
        assert response.json()["color"] == "#3B82F6"

    def test_create_habit_without_name_returns_422(self, client: TestClient):
        """Test validation error for missing name."""
        response = client.post("/api/habits", json={})

        assert response.status_code == 422

    def test_create_habit_with_blank_name_returns_422(self, client: TestClient):
        """Test validation error for blank name."""
        response = client.post("/api/habits", json={"name": "   "})

        assert response.status_code == 422

    def test_create_habit_with_invalid_color_returns_422(self, client: TestClient):
        """Test validation error for invalid color format."""
        response = client.post(
            "/api/habits",
            json={"name": "Test", "color": "red"},
        )

        assert response.status_code == 422

    def test_list_habits_empty(self, client: TestClient):
        """Test listing habits when none exist."""
        response = client.get("/api/habits")

        assert response.status_code == 200
        assert response.json() == {"habits": []}

    def test_list_habits_returns_all(self, client: TestClient):
        """Test listing all habits."""
        client.post("/api/habits", json={"name": "Habit 1"})
        client.post("/api/habits", json={"name": "Habit 2"})

        response = client.get("/api/habits")

        assert response.status_code == 200
        habits = response.json()["habits"]
        assert len(habits) == 2

    def test_list_habits_excludes_archived(self, client: TestClient):
        """Test that archived habits are excluded by default."""
        create_resp = client.post("/api/habits", json={"name": "To Archive"})
        habit_id = create_resp.json()["id"]

        client.patch(f"/api/habits/{habit_id}/archive")

        response = client.get("/api/habits")
        assert len(response.json()["habits"]) == 0

        # But can include archived
        response = client.get("/api/habits?include_archived=true")
        assert len(response.json()["habits"]) == 1

    def test_get_habit_returns_habit(self, client: TestClient):
        """Test getting a specific habit."""
        create_resp = client.post("/api/habits", json={"name": "Test"})
        habit_id = create_resp.json()["id"]

        response = client.get(f"/api/habits/{habit_id}")

        assert response.status_code == 200
        assert response.json()["name"] == "Test"

    def test_get_habit_not_found_returns_404(self, client: TestClient):
        """Test 404 for non-existent habit."""
        response = client.get("/api/habits/99999")

        assert response.status_code == 404

    def test_update_habit(self, client: TestClient):
        """Test updating a habit."""
        create_resp = client.post("/api/habits", json={"name": "Original"})
        habit_id = create_resp.json()["id"]

        response = client.put(
            f"/api/habits/{habit_id}",
            json={"name": "Updated", "description": "New desc"},
        )

        assert response.status_code == 200
        assert response.json()["name"] == "Updated"
        assert response.json()["description"] == "New desc"

    def test_update_habit_partial(self, client: TestClient):
        """Test partial update only changes specified fields."""
        create_resp = client.post(
            "/api/habits",
            json={"name": "Original", "description": "Keep this"},
        )
        habit_id = create_resp.json()["id"]

        response = client.put(
            f"/api/habits/{habit_id}",
            json={"name": "New Name"},
        )

        assert response.status_code == 200
        assert response.json()["name"] == "New Name"
        assert response.json()["description"] == "Keep this"

    def test_delete_habit(self, client: TestClient):
        """Test deleting a habit."""
        create_resp = client.post("/api/habits", json={"name": "To Delete"})
        habit_id = create_resp.json()["id"]

        response = client.delete(f"/api/habits/{habit_id}")

        assert response.status_code == 204

        # Verify deletion
        get_resp = client.get(f"/api/habits/{habit_id}")
        assert get_resp.status_code == 404

    def test_archive_habit(self, client: TestClient):
        """Test archiving a habit."""
        create_resp = client.post("/api/habits", json={"name": "To Archive"})
        habit_id = create_resp.json()["id"]

        response = client.patch(f"/api/habits/{habit_id}/archive")

        assert response.status_code == 200
        assert response.json()["archived_at"] is not None
