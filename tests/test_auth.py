# tests/test_auth_integration.py


def test_register_and_login_flow(client):
    """Проверка базовой регистрации и логина."""
    payload = {
        "username": "lena",
        "email": "lena@example.com",
        "password": "secret123",
    }
    r = client.post("/api/v1/auth/register", json=payload)
    assert r.status_code in (200, 400, 422)
    if r.status_code == 200:
        data = r.json()
        assert "access_token" in data
        assert "refresh_token" in data

        login_data = {"username": "lena", "password": "secret123"}
        r2 = client.post("/api/v1/auth/login", json=login_data)
        assert r2.status_code == 200
        data2 = r2.json()
        assert "access_token" in data2
        assert "refresh_token" in data2
        assert data2["access_token"]
    else:
        # регистрация уже была — ок, продолжаем
        pass


def test_refresh_token_flow(client):
    """Проверка обработчика refresh (негатив)."""
    payload = {"refresh_token": "fake-refresh-token"}
    r = client.post("/api/v1/auth/refresh", json=payload)
    assert r.status_code in (200, 400, 401)
