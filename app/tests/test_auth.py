def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "erik",
            "email": "erik@test.com",
            "password": "123456"
        }
    )
    assert response.status_code == 200
    assert response.json()["username"] == "erik"


def test_login_user(client):
    response = client.post(
        "/auth/login",
        json={
            "username": "erik",
            "password": "123456"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()