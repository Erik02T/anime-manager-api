def get_token(client):
    client.post(
        "/auth/register",
        json={
            "username": "anime_user",
            "email": "anime_user@test.com",
            "password": "abc123"
        }
    )

    response = client.post(
        "/auth/login",
        json={
            "username": "anime_user",
            "password": "abc123"
        }
    )
    return response.json()["access_token"]


def test_create_anime_authenticated(client):
    token = get_token(client)

    response = client.post(
        "/animes",
        json={
            "title": "Naruto",
            "genre": "Shounen",
            "episodes": 220
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Naruto"
