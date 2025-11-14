import uuid

from fastapi.testclient import TestClient


def test_user_endpoints_unauthorized(client: TestClient):

    # GET /user without token -> 403 (HTTPBearer)
    r = client.get("/api/v1/user/")
    assert r.status_code == 403

    # POST /user without token -> 401
    payload = {
        "username": "u" + uuid.uuid4().hex[:6],
        "email": "u@example.com",
        "password": "p",
    }
    r2 = client.post("/api/v1/user/", json=payload)
    assert r2.status_code == 403

    # DELETE /user/1 without token -> 401
    r3 = client.delete("/api/v1/user/1")
    assert r3.status_code == 403
