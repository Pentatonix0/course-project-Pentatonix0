import uuid

from fastapi.testclient import TestClient


def test_dto_extra_fields_rejected_with_problem_json(client: TestClient):
    payload = {
        "username": "v_" + uuid.uuid4().hex[:6],
        "email": "v@example.com",
        "password": "secret123",
        "extra": "forbidden",
    }
    r = client.post("/api/v1/auth/register", json=payload)
    assert r.status_code == 422
    data = r.json()
    # RFC7807 minimal checks
    assert data.get("status") == 422
    assert data.get("title")
    assert "correlation_id" in data
    assert "errors" in data
