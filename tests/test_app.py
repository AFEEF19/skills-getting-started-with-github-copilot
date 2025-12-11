from fastapi.testclient import TestClient
from src.app import app
from urllib.parse import quote


client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # check a few known activities
    assert "Basketball Team" in data
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Art Club"
    email = "teststudent@example.com"

    # ensure clean state: unregister if already present
    client.post(f"/activities/{quote(activity)}/unregister", params={"email": email})

    # signup
    signup = client.post(f"/activities/{quote(activity)}/signup", params={"email": email})
    assert signup.status_code == 200
    assert "Signed up" in signup.json().get("message", "")

    # verify present
    resp = client.get("/activities")
    participants = resp.json()[activity]["participants"]
    assert email in participants

    # unregister
    unreg = client.post(f"/activities/{quote(activity)}/unregister", params={"email": email})
    assert unreg.status_code == 200
    assert "Unregistered" in unreg.json().get("message", "")

    # verify removed
    resp2 = client.get("/activities")
    participants2 = resp2.json()[activity]["participants"]
    assert email not in participants2


def test_signup_already_signed():
    activity = "Programming Class"
    email = "duplicate@example.com"

    # ensure signed up
    client.post(f"/activities/{quote(activity)}/signup", params={"email": email})

    # second signup should fail
    resp = client.post(f"/activities/{quote(activity)}/signup", params={"email": email})
    assert resp.status_code == 400

    # cleanup
    client.post(f"/activities/{quote(activity)}/unregister", params={"email": email})


def test_unregister_not_signed():
    activity = "Soccer Club"
    email = "notregistered@example.com"

    # ensure not signed
    client.post(f"/activities/{quote(activity)}/unregister", params={"email": email})

    # unregister when not signed should return 400
    resp = client.post(f"/activities/{quote(activity)}/unregister", params={"email": email})
    assert resp.status_code == 400
