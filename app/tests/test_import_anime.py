"""
Arquivo: backend/app/tests/test_import_anime.py
Camada: Module
Objetivo: Define responsabilidades deste modulo e sua funcao no sistema.
Dependencias: FastAPI/SQLAlchemy/Pydantic e utilitarios internos conforme necessario.
"""

import uuid

from app import models
from app.external.anime_client import JikanAnimeClient
from app.tests import conftest as test_setup


def create_admin_user_and_headers(client):
    username = f"admin_{uuid.uuid4().hex[:8]}"
    email = f"{username}@test.com"
    password = "abc123"

    register_response = client.post(
        "/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    user_id = register_response.json()["id"]

    db = test_setup.TestingSessionLocal()
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        user.role = "admin"
        db.commit()
    finally:
        db.close()

    login_response = client.post("/auth/login", json={"username": username, "password": password})
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_admin_import_anime_from_external_catalog(client, monkeypatch):
    headers = create_admin_user_and_headers(client)

    def fake_fetch(_self, mal_id: int):
        return {
            "mal_id": mal_id,
            "title": "Cowboy Bebop",
            "genre": "Sci-Fi",
            "episodes": 26,
            "external_score": 9,
            "members": 1000000,
            "external_status": "Finished Airing",
            "image_url": "https://example.com/bebop.jpg",
            "synopsis": "Space bounty hunters.",
        }

    monkeypatch.setattr(JikanAnimeClient, "fetch_anime", fake_fetch)

    response = client.post("/admin/import-anime?mal_id=1", headers=headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] == "jikan"
    assert payload["anime"]["mal_id"] == 1
    assert payload["anime"]["title"] == "Cowboy Bebop"


def test_admin_sync_animes_manual_trigger(client, monkeypatch):
    headers = create_admin_user_and_headers(client)

    def fake_fetch(_self, mal_id: int):
        return {
            "mal_id": mal_id,
            "title": f"Anime {mal_id}",
            "genre": "Action",
            "episodes": 12,
            "external_score": 8,
            "members": 1000,
            "external_status": "Finished Airing",
            "image_url": None,
            "synopsis": "Synopsis",
        }

    monkeypatch.setattr(JikanAnimeClient, "fetch_anime", fake_fetch)

    import_response = client.post("/admin/import-anime?mal_id=2", headers=headers)
    assert import_response.status_code == 200

    sync_response = client.post("/admin/sync-animes?limit=10", headers=headers)
    assert sync_response.status_code == 200
    assert sync_response.json()["synced_count"] >= 1



