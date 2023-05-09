from fastapi.testclient import TestClient

from src.api.server import app

client = TestClient(app)


def test_users():
    response = client.get("/users/")
    assert response.status_code == 200


def test_users_by_id():
    response = client.get("/users/9/")
    assert response.status_code == 200
    assert response.json() == {"user_id": 9, "name": "testing"}


def test_users_by_id2():
    response = client.get("/users/99999999999/")
    assert response.status_code == 404
    assert response.json() == {"detail": "user not found."}


def test_basic_user_post():
    data = {
        "name": "test_user"
    }

    postResponse = client.post("/users/", json=data)
    assert postResponse.status_code == 200
    assert "user_id" in postResponse.json()
    assert postResponse.json()["user_name"] == "test_user"
