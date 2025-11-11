# tests/test_quiz.py
import os
import uuid

from fastapi.testclient import TestClient
from jose import jwt


def _register_and_login(client: TestClient):
    username = "qa_" + uuid.uuid4().hex[:6]
    email = f"{username}@example.com"
    password = "secret123"

    r = client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    assert r.status_code in (200, 400, 422)

    r2 = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    assert r2.status_code == 200
    data = r2.json()
    return data["access_token"], username


def _user_id_from_token(token: str) -> int:
    secret = os.getenv("SECRET_KEY", "default-insecure-key")
    data = jwt.decode(token, secret, algorithms=["HS256"])
    return int(data["sub"])  # user_id


def test_quiz_flow_and_negatives(client: TestClient):
    # Unauthorized calls
    r_unauth_list = client.get("/api/v1/quizzes/")
    assert r_unauth_list.status_code == 403

    r_unauth_create = client.post(
        "/api/v1/quizzes/", json={"author_id": 1, "name": "n", "description": "d"}
    )
    assert r_unauth_create.status_code == 403

    # Authenticated flow
    access_token, username = _register_and_login(client)
    headers = {"Authorization": f"Bearer {access_token}"}
    user_id = _user_id_from_token(access_token)

    # Negative: non-existent author
    bad = client.post(
        "/api/v1/quizzes/",
        headers=headers,
        json={"author_id": 999999, "name": "Sample", "description": "Desc"},
    )
    assert bad.status_code in (404, 401)

    # Create quiz
    r_create = client.post(
        "/api/v1/quizzes/",
        headers=headers,
        json={"author_id": user_id, "name": "Sample", "description": "Desc"},
    )
    assert r_create.status_code == 200

    # List quizzes
    r_list = client.get("/api/v1/quizzes/", headers=headers)
    assert r_list.status_code == 200
    items = r_list.json()
    assert isinstance(items, list)
    assert any(q.get("name") == "Sample" for q in items)
    quiz_id = items[0]["model_id"]

    # Preview quiz
    r_prev = client.get(f"/api/v1/quizzes/{quiz_id}/preview", headers=headers)
    assert r_prev.status_code == 200

    # Update quiz
    r_upd = client.put(
        f"/api/v1/quizzes/{quiz_id}",
        headers=headers,
        json={"name": "Updated", "description": "New"},
    )
    assert r_upd.status_code in (200, 422)

    # Delete quiz
    r_del = client.delete(f"/api/v1/quizzes/{quiz_id}", headers=headers)
    assert r_del.status_code == 200
