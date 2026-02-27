import uuid

import jwt

from app.core.config import settings
from app.core import rate_limit


def create_user(client, prefix: str):
    username = f"{prefix}_{uuid.uuid4().hex[:8]}"
    email = f"{username}@test.com"
    password = "abc123"
    response = client.post("/auth/register", json={"username": username, "email": email, "password": password})
    assert response.status_code == 200
    return username, password


def test_invalid_jwt_issuer_or_audience_rejected(client):
    username, _password = create_user(client, "jwt_invalid")

    token = jwt.encode(
        {
            "sub": username,
            "iss": "wrong-issuer",
            "aud": "wrong-audience",
        },
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    response = client.get("/animes", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


def test_auth_rate_limit_returns_429(client):
    rate_limit.rate_limiter._hits.clear()

    username, password = create_user(client, "rate_limit")

    # Consume auth/login budget quickly from same client IP.
    for _ in range(settings.AUTH_RATE_LIMIT_PER_MINUTE):
        response = client.post("/auth/login", json={"username": username, "password": password})
        assert response.status_code == 200

    blocked = client.post("/auth/login", json={"username": username, "password": password})
    assert blocked.status_code == 429
