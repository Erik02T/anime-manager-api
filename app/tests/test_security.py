import uuid

from app import models
from app.tests import conftest as test_setup


def create_user_and_token(client, prefix: str):
    username = f"{prefix}_{uuid.uuid4().hex[:8]}"
    email = f"{username}@test.com"
    password = "abc123"

    register_response = client.post(
        "/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    user_id = register_response.json()["id"]

    login_response = client.post(
        "/auth/login",
        json={"username": username, "password": password},
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return user_id, headers


def test_forbidden_cross_user_user_anime_create(client):
    owner_id, owner_headers = create_user_and_token(client, "sec_owner")
    attacker_id, attacker_headers = create_user_and_token(client, "sec_attacker")

    anime_response = client.post(
        "/animes",
        json={"title": "Berserk", "genre": "Seinen", "episodes": 25},
        headers=owner_headers,
    )
    anime_id = anime_response.json()["id"]

    response = client.post(
        "/user-animes",
        json={
            "user_id": owner_id,
            "anime_id": anime_id,
            "status": "watching",
            "score": 9,
            "episodes_watched": 2,
        },
        headers=attacker_headers,
    )
    assert attacker_id != owner_id
    assert response.status_code == 403


def test_forbidden_cross_user_stats_access(client):
    user_id, _ = create_user_and_token(client, "sec_stats_owner")
    _, attacker_headers = create_user_and_token(client, "sec_stats_attacker")

    response = client.get(f"/stats/users/{user_id}", headers=attacker_headers)
    assert response.status_code == 403


def test_admin_role_enforced_and_metrics_available(client):
    user_id, headers = create_user_and_token(client, "sec_admin")

    forbidden_response = client.get("/admin/users", headers=headers)
    assert forbidden_response.status_code == 403

    db = test_setup.TestingSessionLocal()
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        user.role = "admin"
        db.commit()
    finally:
        db.close()

    allowed_response = client.get("/admin/users", headers=headers)
    assert allowed_response.status_code == 200
    assert isinstance(allowed_response.json(), list)

    metrics_response = client.get("/metrics")
    assert metrics_response.status_code == 200
    assert "anime_manager_http_requests_total" in metrics_response.text
