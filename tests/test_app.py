import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
_initial = copy.deepcopy(activities)

@pytest.fixture(autouse=True)
def reset_activities():
    # Reset in-memory activities before each test
    activities.clear()
    activities.update(copy.deepcopy(_initial))
    yield


def test_get_activities():
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_and_duplicate():
    email = "testuser@example.com"
    r = client.post(f"/activities/{quote('Chess Club')}/signup?email={email}")
    assert r.status_code == 200
    assert "Signed up" in r.json()["message"]

    # Verify added
    r2 = client.get("/activities")
    assert email in r2.json()["Chess Club"]["participants"]

    # Duplicate signup should fail
    r3 = client.post(f"/activities/{quote('Chess Club')}/signup?email={email}")
    assert r3.status_code == 400


def test_unregister():
    email = "john@mergington.edu"
    r = client.delete(f"/activities/{quote('Gym Class')}/participants?email={email}")
    assert r.status_code == 200

    r2 = client.get("/activities")
    assert email not in r2.json()["Gym Class"]["participants"]

    # Unregister non-existing participant
    r3 = client.delete(f"/activities/{quote('Gym Class')}/participants?email=nonexistent@example.com")
    assert r3.status_code == 404


def test_signup_unknown_activity():
    r = client.post(f"/activities/{quote('Nonexistent')}/signup?email=a@b.com")
    assert r.status_code == 404


def test_unregister_unknown_activity():
    r = client.delete(f"/activities/{quote('Nonexistent')}/participants?email=a@b.com")
    assert r.status_code == 404
