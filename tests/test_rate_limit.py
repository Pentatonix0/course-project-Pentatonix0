import uuid

from fastapi.testclient import TestClient


def test_login_rate_limit_triggers_under_load(client: TestClient):
    username = "rl_" + uuid.uuid4().hex[:6]
    email = f"{username}@example.com"
    password = "secret123"

    # register
    r = client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    assert r.status_code in (200, 400, 422)

    # make 6 quick login attempts to cross 5/min/IP threshold
    statuses = []
    for i in range(6):
        resp = client.post(
            "/api/v1/auth/login", json={"username": username, "password": "wrong"}
        )
        statuses.append(resp.status_code)

    # Expect at least one 429 (rate limit) among responses
    assert 429 in statuses
