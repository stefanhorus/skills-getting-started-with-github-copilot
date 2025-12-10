"""Tests for FastAPI endpoints."""

import pytest


class TestRootEndpoint:
    """Test the root endpoint redirect."""

    def test_root_redirects_to_static_html(self, client):
        """Test that GET / redirects to /static/index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Test the activities listing endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities."""
        response = client.get("/activities")
        assert response.status_code == 200

        activities = response.json()
        assert isinstance(activities, dict)

        # Verify expected activities are present
        expected_activities = [
            "Chess Club",
            "Soccer Team",
            "Basketball Club",
            "Drama Club",
            "Art Workshop",
            "Math Club",
            "Science Olympiad",
            "Programming Class",
            "Gym Class",
        ]
        for activity in expected_activities:
            assert activity in activities

    def test_activity_structure(self, client):
        """Test that each activity has the correct structure."""
        response = client.get("/activities")
        activities = response.json()

        for name, details in activities.items():
            assert "description" in details
            assert "schedule" in details
            assert "max_participants" in details
            assert "participants" in details
            assert isinstance(details["participants"], list)

    def test_activities_have_initial_participants(self, client):
        """Test that activities have initial participants."""
        response = client.get("/activities")
        activities = response.json()

        # Chess Club should have 2 participants
        assert len(activities["Chess Club"]["participants"]) == 2
        assert "michael@mergington.edu" in activities["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in activities["Chess Club"]["participants"]


class TestSignupEndpoint:
    """Test the signup endpoint."""

    def test_signup_new_participant(self, client):
        """Test signing up a new participant for an activity."""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu",
            follow_redirects=False,
        )
        assert response.status_code == 200

        result = response.json()
        assert "message" in result
        assert "newstudent@mergington.edu" in result["message"]

        # Verify participant was added
        activities = client.get("/activities").json()
        assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]

    def test_signup_duplicate_participant_fails(self, client):
        """Test that signing up the same participant twice fails."""
        email = "michael@mergington.edu"

        # First signup should succeed
        response = client.post(
            f"/activities/Chess%20Club/signup?email={email}",
        )
        assert response.status_code == 200

        # Second signup with same email should fail
        response = client.post(
            f"/activities/Chess%20Club/signup?email={email}",
        )
        assert response.status_code == 400
        result = response.json()
        assert "already signed up" in result["detail"].lower()

    def test_signup_nonexistent_activity_fails(self, client):
        """Test that signing up for a non-existent activity fails."""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        result = response.json()
        assert "not found" in result["detail"].lower()

    def test_signup_with_special_characters_in_email(self, client):
        """Test signup with valid email containing special characters."""
        email = "john.doe+test@mergington.edu"
        response = client.post(
            f"/activities/Chess%20Club/signup?email={email}",
        )
        assert response.status_code == 200

        # Verify participant was added
        activities = client.get("/activities").json()
        assert email in activities["Chess Club"]["participants"]

    def test_signup_with_spaces_in_activity_name(self, client):
        """Test signup with activity names containing spaces."""
        response = client.post(
            "/activities/Soccer%20Team/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200

        activities = client.get("/activities").json()
        assert "test@mergington.edu" in activities["Soccer Team"]["participants"]


class TestUnregisterEndpoint:
    """Test the unregister/delete participant endpoint."""

    def test_unregister_existing_participant(self, client):
        """Test unregistering an existing participant."""
        email = "michael@mergington.edu"
        activity = "Chess Club"

        # Verify participant is registered
        activities = client.get("/activities").json()
        assert email in activities[activity]["participants"]

        # Unregister the participant
        response = client.delete(
            f"/activities/{activity}/participants?email={email}"
        )
        assert response.status_code == 200
        result = response.json()
        assert "Unregistered" in result["message"]

        # Verify participant was removed
        activities = client.get("/activities").json()
        assert email not in activities[activity]["participants"]

    def test_unregister_nonexistent_participant_fails(self, client):
        """Test that unregistering a participant not in the activity fails."""
        response = client.delete(
            "/activities/Chess%20Club/participants?email=notregistered@mergington.edu"
        )
        assert response.status_code == 404
        result = response.json()
        assert "not signed up" in result["detail"].lower()

    def test_unregister_from_nonexistent_activity_fails(self, client):
        """Test that unregistering from a non-existent activity fails."""
        response = client.delete(
            "/activities/Nonexistent/participants?email=test@mergington.edu"
        )
        assert response.status_code == 404
        result = response.json()
        assert "not found" in result["detail"].lower()

    def test_unregister_then_signup_same_participant(self, client):
        """Test that a participant can re-signup after being unregistered."""
        email = "michael@mergington.edu"
        activity = "Chess Club"

        # Unregister
        response = client.delete(
            f"/activities/{activity}/participants?email={email}"
        )
        assert response.status_code == 200

        # Sign up again
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert response.status_code == 200

        # Verify participant is registered again
        activities = client.get("/activities").json()
        assert email in activities[activity]["participants"]

    def test_unregister_with_spaces_in_activity_name(self, client):
        """Test unregister with activity names containing spaces."""
        email = "michael@mergington.edu"

        response = client.delete(
            "/activities/Chess%20Club/participants?email=michael@mergington.edu"
        )
        assert response.status_code == 200

        activities = client.get("/activities").json()
        assert email not in activities["Chess Club"]["participants"]


class TestIntegrationScenarios:
    """Integration tests combining multiple operations."""

    def test_full_signup_and_unregister_flow(self, client):
        """Test the complete flow: signup, list, unregister, list."""
        email = "integration@mergington.edu"
        activity = "Basketball Club"

        # Sign up
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200

        # Verify in list
        activities = client.get("/activities").json()
        assert email in activities[activity]["participants"]

        # Unregister
        response = client.delete(f"/activities/{activity}/participants?email={email}")
        assert response.status_code == 200

        # Verify not in list
        activities = client.get("/activities").json()
        assert email not in activities[activity]["participants"]

    def test_multiple_signups_same_activity(self, client):
        """Test multiple different participants signing up for the same activity."""
        activity = "Drama Club"
        emails = ["test1@mergington.edu", "test2@mergington.edu", "test3@mergington.edu"]

        for email in emails:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200

        # Verify all are registered
        activities = client.get("/activities").json()
        for email in emails:
            assert email in activities[activity]["participants"]

    def test_participant_count_decreases_on_unregister(self, client):
        """Test that participant count decreases when someone unregisters."""
        activity = "Art Workshop"
        email = "amelia@mergington.edu"

        # Get initial count
        initial_activities = client.get("/activities").json()
        initial_count = len(initial_activities[activity]["participants"])

        # Unregister
        response = client.delete(f"/activities/{activity}/participants?email={email}")
        assert response.status_code == 200

        # Check new count
        updated_activities = client.get("/activities").json()
        new_count = len(updated_activities[activity]["participants"])

        assert new_count == initial_count - 1

    def test_signup_changes_reflected_immediately(self, client):
        """Test that signup changes are reflected immediately in API response."""
        activity = "Science Olympiad"
        email = "immediate@mergington.edu"

        # Sign up
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200

        # Immediately fetch activities
        response = client.get("/activities")
        activities = response.json()

        # Verify participant is in the list immediately
        assert email in activities[activity]["participants"]
