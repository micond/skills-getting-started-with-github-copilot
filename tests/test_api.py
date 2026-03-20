"""Backend API endpoint tests using Arrange-Act-Assert pattern"""

import pytest


class TestRootEndpoint:
    """Tests for GET / endpoint"""

    def test_root_redirects_to_static_index(self, client):
        """Root path should redirect to static/index.html"""
        # Arrange
        expected_redirect_url = "/static/index.html"

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_redirect_url


class TestActivitiesEndpoint:
    """Tests for GET /activities endpoint"""

    def test_get_all_activities_returns_dict(self, client):
        """Should return a dictionary of all activities"""
        # Arrange
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Tennis Club",
            "Art Studio",
            "Music Ensemble",
            "Debate Club",
            "Science Club",
        ]

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        for activity_name in expected_activities:
            assert activity_name in activities

    def test_activity_has_required_fields(self, client):
        """Each activity should have required fields"""
        # Arrange
        required_fields = {
            "description",
            "schedule",
            "max_participants",
            "participants",
        }

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            for field in required_fields:
                assert field in activity_data, f"Missing field '{field}' in {activity_name}"

    def test_participants_is_list(self, client):
        """Participants field should be a list"""
        # Arrange
        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(
                activity_data["participants"], list
            ), f"Participants for {activity_name} is not a list"


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_participant_success(self, client):
        """Should successfully sign up a new participant"""
        # Arrange
        activity_name = "Chess Club"
        new_email = "newcomer@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={new_email}"
        )

        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert new_email in result["message"]
        assert activity_name in result["message"]

    def test_signup_duplicate_participant_fails(self, client):
        """Should reject signup for participant already registered"""
        # Arrange
        activity_name = "Chess Club"
        existing_participant = "michael@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={existing_participant}"
        )

        # Assert
        assert response.status_code == 400
        result = response.json()
        assert "detail" in result
        assert "already signed up" in result["detail"]

    def test_signup_to_nonexistent_activity_fails(self, client):
        """Should reject signup for activity that does not exist"""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "test@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "not found" in result["detail"]

    def test_signup_updates_activities_list(self, client):
        """Signup should add participant to activity's participants list"""
        # Arrange
        activity_name = "Programming Class"
        new_email = "signup_test@mergington.edu"

        # Act
        client.post(f"/activities/{activity_name}/signup?email={new_email}")
        response = client.get("/activities")

        # Assert
        activities = response.json()
        assert new_email in activities[activity_name]["participants"]


class TestUnregisterEndpoint:
    """Tests for DELETE /activities/{activity_name}/participants endpoint"""

    def test_unregister_existing_participant_success(self, client):
        """Should successfully unregister an existing participant"""
        # Arrange
        activity_name = "Chess Club"
        participant_to_remove = "michael@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants?email={participant_to_remove}"
        )

        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert participant_to_remove in result["message"]
        assert activity_name in result["message"]

    def test_unregister_removes_from_participants_list(self, client):
        """Unregister should remove participant from activity's list"""
        # Arrange
        activity_name = "Chess Club"
        participant_to_remove = "daniel@mergington.edu"

        # Act
        client.delete(
            f"/activities/{activity_name}/participants?email={participant_to_remove}"
        )
        response = client.get("/activities")

        # Assert
        activities = response.json()
        assert participant_to_remove not in activities[activity_name]["participants"]

    def test_unregister_nonexistent_participant_fails(self, client):
        """Should reject unregister for participant not in activity"""
        # Arrange
        activity_name = "Art Studio"
        nonexistent_participant = "notinlist@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants?email={nonexistent_participant}"
        )

        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "not found" in result["detail"]

    def test_unregister_from_nonexistent_activity_fails(self, client):
        """Should reject unregister for activity that does not exist"""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "someone@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants?email={email}"
        )

        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "not found" in result["detail"]

    def test_unregister_and_signup_again(self, client):
        """Should be able to signup again after unregistering"""
        # Arrange
        activity_name = "Tennis Club"
        test_email = "retest@mergington.edu"

        # Act - First signup
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={test_email}"
        )
        assert signup_response.status_code == 200

        # Act - Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/participants?email={test_email}"
        )
        assert unregister_response.status_code == 200

        # Act - Signup again
        signup_again_response = client.post(
            f"/activities/{activity_name}/signup?email={test_email}"
        )

        # Assert
        assert signup_again_response.status_code == 200
        result = signup_again_response.json()
        assert test_email in result["message"]
