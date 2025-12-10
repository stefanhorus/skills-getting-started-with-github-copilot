"""Pytest configuration and fixtures for FastAPI tests."""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Return a TestClient for the FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data to initial state before each test."""
    from src import app as app_module

    # Store original activities
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
        },
        "Soccer Team": {
            "description": "Join the school soccer team for training and matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["lucas@mergington.edu", "mia@mergington.edu"],
        },
        "Basketball Club": {
            "description": "Practice basketball skills and compete in games",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["liam@mergington.edu", "ava@mergington.edu"],
        },
        "Drama Club": {
            "description": "Participate in theater productions and acting workshops",
            "schedule": "Mondays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["noah@mergington.edu", "isabella@mergington.edu"],
        },
        "Art Workshop": {
            "description": "Explore painting, drawing, and other visual arts",
            "schedule": "Fridays, 2:00 PM - 3:30 PM",
            "max_participants": 20,
            "participants": ["amelia@mergington.edu", "ethan@mergington.edu"],
        },
        "Math Club": {
            "description": "Solve challenging math problems and prepare for competitions",
            "schedule": "Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 16,
            "participants": ["charlotte@mergington.edu", "jack@mergington.edu"],
        },
        "Science Olympiad": {
            "description": "Engage in science projects and compete in science events",
            "schedule": "Wednesdays, 4:00 PM - 5:00 PM",
            "max_participants": 14,
            "participants": ["benjamin@mergington.edu", "harper@mergington.edu"],
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"],
        },
    }

    # Reset to original state
    app_module.activities.clear()
    app_module.activities.update(original_activities)

    yield

    # Cleanup (optional, since we reset at the start of next test)
    app_module.activities.clear()
    app_module.activities.update(original_activities)
