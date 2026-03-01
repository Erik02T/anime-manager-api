"""
Arquivo: backend/app/tests/test_stats.py
Camada: Module
Objetivo: Define responsabilidades deste modulo e sua funcao no sistema.
Dependencias: FastAPI/SQLAlchemy/Pydantic e utilitarios internos conforme necessario.
"""

import uuid


def setup_stats_data(client):
    unique = uuid.uuid4().hex[:8]
    username = f"stats_user_{unique}"
    email = f"{username}@test.com"

    register_response = client.post(
        "/auth/register",
        json={
            "username": username,
            "email": email,
            "password": "abc123",
        },
    )
    user_id = register_response.json()["id"]

    login_response = client.post(
        "/auth/login",
        json={
            "username": username,
            "password": "abc123",
        },
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    anime_a = client.post(
        "/animes",
        json={"title": "Attack on Titan", "genre": "Action", "episodes": 87},
        headers=headers,
    ).json()
    anime_b = client.post(
        "/animes",
        json={"title": "Death Note", "genre": "Thriller", "episodes": 37},
        headers=headers,
    ).json()

    client.post(
        "/user-animes",
        json={
            "user_id": user_id,
            "anime_id": anime_a["id"],
            "status": "completed",
            "score": 10,
            "episodes_watched": 87,
        },
        headers=headers,
    )
    client.post(
        "/user-animes",
        json={
            "user_id": user_id,
            "anime_id": anime_b["id"],
            "status": "watching",
            "score": 8,
            "episodes_watched": 20,
        },
        headers=headers,
    )

    return user_id, headers


def test_user_stats(client):
    user_id, headers = setup_stats_data(client)

    response = client.get(f"/stats/users/{user_id}", headers=headers)
    assert response.status_code == 200

    payload = response.json()
    assert payload["average_score"] == 9.0
    assert payload["total_watched_episodes"] == 107
    assert payload["total_completed"] == 1
    assert len(payload["personal_ranking"]) == 2
    assert payload["personal_ranking"][0]["score"] == 10


def test_global_stats(client):
    _, headers = setup_stats_data(client)

    response = client.get("/stats/global", headers=headers)
    assert response.status_code == 200

    payload = response.json()
    assert len(payload["average_scores"]) >= 2
    assert payload["most_watched"] is not None
    assert payload["best_rated"] is not None



