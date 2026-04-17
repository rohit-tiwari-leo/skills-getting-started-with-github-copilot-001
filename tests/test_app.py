from copy import deepcopy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
INITIAL_ACTIVITIES = deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(deepcopy(INITIAL_ACTIVITIES))


def test_get_activities_returns_all_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_for_activity_adds_participant():
    activity_name = "Programming Class"
    new_email = "newstudent@mergington.edu"
    response = client.post(
        f"/activities/{quote(activity_name, safe='')}/signup",
        params={"email": new_email},
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {new_email} for {activity_name}"}
    assert new_email in activities[activity_name]["participants"]


def test_signup_for_activity_fails_for_duplicate_email():
    activity_name = "Chess Club"
    existing_email = activities[activity_name]["participants"][0]

    response = client.post(
        f"/activities/{quote(activity_name, safe='')}/signup",
        params={"email": existing_email},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_remove_activity_participant_unregisters_user():
    activity_name = "Gym Class"
    existing_email = activities[activity_name]["participants"][0]

    response = client.delete(
        f"/activities/{quote(activity_name, safe='')}/participants",
        params={"email": existing_email},
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {existing_email} from {activity_name}"}
    assert existing_email not in activities[activity_name]["participants"]


def test_remove_participant_returns_404_for_missing_participant():
    activity_name = "Drama Club"
    missing_email = "notfound@mergington.edu"

    response = client.delete(
        f"/activities/{quote(activity_name, safe='')}/participants",
        params={"email": missing_email},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
