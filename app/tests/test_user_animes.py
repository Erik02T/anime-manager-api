"""
Arquivo: backend/app/tests/test_user_animes.py
Camada: Module
Objetivo: Define responsabilidades deste modulo e sua funcao no sistema.
Dependencias: FastAPI/SQLAlchemy/Pydantic e utilitarios internos conforme necessario.
"""

import uuid


def get_auth_context(client):
    unique = uuid.uuid4().hex[:8]
    username = f"ua_user_{unique}"
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

    anime_response = client.post(
        "/animes",
        json={
            "title": "One Piece",
            "genre": "Shounen",
            "episodes": 1100,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    anime_id = anime_response.json()["id"]

    return user_id, anime_id, token


def test_create_user_anime_and_prevent_duplicate(client):
    user_id, anime_id, token = get_auth_context(client)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/user-animes",
        json={
            "user_id": user_id,
            "anime_id": anime_id,
            "status": "watching",
            "score": 9,
            "episodes_watched": 120,
        },
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["user_id"] == user_id
    assert response.json()["anime_id"] == anime_id
    assert response.json()["status"] == "watching"

    duplicate_response = client.post(
        "/user-animes",
        json={
            "user_id": user_id,
            "anime_id": anime_id,
            "status": "completed",
            "score": 10,
            "episodes_watched": 1100,
        },
        headers=headers,
    )

    assert duplicate_response.status_code == 400


def test_patch_user_anime_increment_progress_and_score(client):
    user_id, anime_id, token = get_auth_context(client)
    headers = {"Authorization": f"Bearer {token}"}

    create_response = client.post(
        "/user-animes",
        json={
            "user_id": user_id,
            "anime_id": anime_id,
            "status": "watching",
            "score": 7,
            "episodes_watched": 100,
        },
        headers=headers,
    )
    entry_id = create_response.json()["id"]

    patch_response = client.patch(
        f"/user-animes/{entry_id}",
        json={
            "episodes_increment": 20,
            "score": 8,
            "status": "watching",
        },
        headers=headers,
    )

    assert patch_response.status_code == 200
    assert patch_response.json()["episodes_watched"] == 120
    assert patch_response.json()["score"] == 8


def test_patch_user_anime_rejects_progress_above_total(client):
    user_id, anime_id, token = get_auth_context(client)
    headers = {"Authorization": f"Bearer {token}"}

    create_response = client.post(
        "/user-animes",
        json={
            "user_id": user_id,
            "anime_id": anime_id,
            "status": "watching",
            "score": 7,
            "episodes_watched": 1090,
        },
        headers=headers,
    )
    entry_id = create_response.json()["id"]

    patch_response = client.patch(
        f"/user-animes/{entry_id}",
        json={"episodes_increment": 20},
        headers=headers,
    )

    assert patch_response.status_code == 400


def test_patch_user_anime_with_absolute_progress(client):
    user_id, anime_id, token = get_auth_context(client)
    headers = {"Authorization": f"Bearer {token}"}

    create_response = client.post(
        "/user-animes",
        json={
            "user_id": user_id,
            "anime_id": anime_id,
            "status": "watching",
            "score": 6,
            "episodes_watched": 10,
        },
        headers=headers,
    )
    entry_id = create_response.json()["id"]

    patch_response = client.patch(
        f"/user-animes/{entry_id}",
        json={
            "episodes_watched": 300,
            "score": 9,
            "status": "watching",
        },
        headers=headers,
    )

    assert patch_response.status_code == 200
    assert patch_response.json()["episodes_watched"] == 300
    assert patch_response.json()["score"] == 9


def test_patch_user_anime_rejects_mixed_progress_modes(client):
    user_id, anime_id, token = get_auth_context(client)
    headers = {"Authorization": f"Bearer {token}"}

    create_response = client.post(
        "/user-animes",
        json={
            "user_id": user_id,
            "anime_id": anime_id,
            "status": "watching",
            "score": 7,
            "episodes_watched": 100,
        },
        headers=headers,
    )
    entry_id = create_response.json()["id"]

    patch_response = client.patch(
        f"/user-animes/{entry_id}",
        json={
            "episodes_watched": 200,
            "episodes_increment": 10,
        },
        headers=headers,
    )

    assert patch_response.status_code == 400



