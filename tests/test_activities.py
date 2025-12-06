from fastapi.testclient import TestClient
import copy

from src import app as app_module

client = TestClient(app_module.app)

# Keep a pristine copy of the initial activities to reset between tests
ORIGINAL_ACTIVITIES = copy.deepcopy(app_module.activities)


def setup_function():
    # Reset activities to original state before each test
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_duplicate_rejection():
    email = "tester@example.com"
    activity = "Chess Club"

    # Ensure not already present
    assert email not in app_module.activities[activity]["participants"]

    # Signup should succeed
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert resp.json()["message"] == f"Signed up {email} for {activity}"
    assert email in app_module.activities[activity]["participants"]

    # Duplicate signup should be rejected (400)
    resp2 = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp2.status_code == 400
    assert "already" in resp2.json()["detail"].lower()


def test_unregister_participant():
    email = "to_remove@example.com"
    activity = "Programming Class"

    # Add participant first
    app_module.activities[activity]["participants"].append(email)
    assert email in app_module.activities[activity]["participants"]

    # Unregister should succeed
    resp = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert resp.status_code == 200
    assert resp.json()["message"] == f"Unregistered {email} from {activity}"
    assert email not in app_module.activities[activity]["participants"]

    # Unregistering again should return 404
    resp2 = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert resp2.status_code == 404


def test_signup_nonexistent_activity():
    resp = client.post("/activities/NoSuchActivity/signup", params={"email": "a@b.com"})
    assert resp.status_code == 404


def test_unregister_nonexistent_activity():
    resp = client.delete("/activities/NoSuchActivity/participants", params={"email": "a@b.com"})
    assert resp.status_code == 404
