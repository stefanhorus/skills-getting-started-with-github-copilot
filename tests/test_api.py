from fastapi.testclient import TestClient
import copy
import pytest

from src.app import app, activities


client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    # keep a copy of the original in-memory data and restore after each test
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Basic sanity: some known activities should exist
    assert "Chess Club" in data


def test_signup_and_list_update():
    activity = "Chess Club"
    email = "test_student@example.com"

    # Ensure not already present
    assert email not in activities[activity]["participants"]

    # Sign up via POST (email as query param)
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    body = resp.json()
    assert "Signed up" in body.get("message", "")

    # Verify that the in-memory activities were updated
    assert email in activities[activity]["participants"]


def test_unregister_participant():
    activity = "Chess Club"
    email = "remove_me@example.com"

    # Add participant first
    activities[activity]["participants"].append(email)
    assert email in activities[activity]["participants"]

    # Call DELETE endpoint
    resp = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert resp.status_code == 200
    data = resp.json()
    assert "Unregistered" in data.get("message", "")

    # Ensure it's removed
    assert email not in activities[activity]["participants"]
