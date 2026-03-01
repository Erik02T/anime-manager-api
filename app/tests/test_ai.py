from app.external.anime_client import JikanAnimeClient


def create_user_and_token(client, suffix: str = "ai"):
    username = f"{suffix}_user"
    email = f"{suffix}@test.com"
    password = "abc123"
    register_response = client.post(
        "/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    assert register_response.status_code == 200

    login_response = client.post("/auth/login", json={"username": username, "password": password})
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    user_id = register_response.json()["id"]
    return user_id, {"Authorization": f"Bearer {token}"}


def test_ai_recommendations_news_and_auto_status(client, monkeypatch):
    def fake_top(_self, limit: int = 25):
        return [
            {
                "mal_id": 101,
                "title": "AI Top Anime",
                "genre": "Action, Adventure",
                "episodes": 12,
                "external_score": 9,
                "members": 100000,
                "external_status": "Airing",
                "image_url": None,
                "synopsis": "Top anime from fake feed",
                "aired_from": None,
                "url": "https://example.com/top",
            }
        ]

    def fake_season(_self, limit: int = 25):
        return [
            {
                "mal_id": 202,
                "title": "AI Season Anime",
                "genre": "Action, Fantasy",
                "episodes": 24,
                "external_score": 8,
                "members": 70000,
                "external_status": "Airing",
                "image_url": None,
                "synopsis": "Season anime from fake feed",
                "aired_from": None,
                "url": "https://example.com/season",
            }
        ]

    def fake_upcoming(_self, limit: int = 20):
        return [
            {
                "mal_id": 303,
                "title": "Upcoming AI Anime",
                "genre": "Sci-Fi",
                "episodes": 13,
                "external_score": 8,
                "members": 50000,
                "external_status": "Not yet aired",
                "image_url": None,
                "synopsis": "Upcoming anime from fake feed",
                "aired_from": None,
                "url": "https://example.com/upcoming",
            }
        ]

    monkeypatch.setattr(JikanAnimeClient, "fetch_top_anime", fake_top)
    monkeypatch.setattr(JikanAnimeClient, "fetch_current_season", fake_season)
    monkeypatch.setattr(JikanAnimeClient, "fetch_upcoming", fake_upcoming)

    user_id, headers = create_user_and_token(client, "ai1")

    rec_response = client.get("/ai/recommendations?limit=5", headers=headers)
    assert rec_response.status_code == 200
    assert len(rec_response.json()) >= 1

    news_response = client.get("/ai/news?limit=5", headers=headers)
    assert news_response.status_code == 200
    assert len(news_response.json()) >= 1
    assert news_response.json()[0]["title"] == "Upcoming AI Anime"

    create_anime_response = client.post(
        "/animes/",
        headers=headers,
        json={"title": "My Anime", "genre": "Action", "episodes": 12},
    )
    assert create_anime_response.status_code == 200
    anime_id = create_anime_response.json()["id"]

    create_entry_response = client.post(
        "/user-animes/",
        headers=headers,
        json={
            "user_id": user_id,
            "anime_id": anime_id,
            "status": "planned",
            "episodes_watched": 12,
        },
    )
    assert create_entry_response.status_code == 200

    auto_status_response = client.post("/ai/auto-status", headers=headers)
    assert auto_status_response.status_code == 200
    assert auto_status_response.json()["updated_count"] >= 1
