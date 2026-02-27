import uuid


def create_user_and_token(client, suffix: str):
    username = f"user_{suffix}_{uuid.uuid4().hex[:6]}"
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


def test_social_review_feed_and_dashboard(client):
    user_1_id, user_1_headers = create_user_and_token(client, "social1")
    user_2_id, user_2_headers = create_user_and_token(client, "social2")

    anime_response = client.post(
        "/animes",
        json={"title": "Bleach", "genre": "Shounen", "episodes": 366},
        headers=user_1_headers,
    )
    anime_id = anime_response.json()["id"]

    client.post(
        "/user-animes",
        json={
            "user_id": user_1_id,
            "anime_id": anime_id,
            "status": "watching",
            "score": 8,
            "episodes_watched": 50,
        },
        headers=user_1_headers,
    )

    review_response = client.post(
        "/social/reviews",
        json={
            "user_id": user_1_id,
            "anime_id": anime_id,
            "score": 9,
            "content": "Great pacing and fights.",
        },
        headers=user_1_headers,
    )
    assert review_response.status_code == 200
    review_id = review_response.json()["id"]

    follow_response = client.post(
        "/social/follow",
        json={"follower_id": user_2_id, "following_id": user_1_id},
        headers=user_2_headers,
    )
    assert follow_response.status_code == 200

    comment_response = client.post(
        f"/social/reviews/{review_id}/comments",
        json={"user_id": user_2_id, "content": "Concordo!"},
        headers=user_2_headers,
    )
    assert comment_response.status_code == 200

    feed_response = client.get(f"/social/feed/{user_2_id}", headers=user_2_headers)
    assert feed_response.status_code == 200
    feed = feed_response.json()
    assert any(item["activity_type"] == "review_created" for item in feed)

    dashboard_response = client.get(f"/social/dashboard/{user_1_id}", headers=user_1_headers)
    assert dashboard_response.status_code == 200
    dashboard = dashboard_response.json()
    assert dashboard["followers_count"] >= 1
    assert "user_stats" in dashboard
