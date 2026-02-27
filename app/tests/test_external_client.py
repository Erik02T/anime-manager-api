import httpx

from app.external.anime_client import JikanAnimeClient


class DummyResponse:
    def __init__(self, status_code: int, payload: dict | None = None, headers: dict | None = None):
        self.status_code = status_code
        self._payload = payload or {}
        self.headers = headers or {}
        self.request = httpx.Request("GET", "https://example.com")

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("error", request=self.request, response=httpx.Response(self.status_code))


def test_jikan_client_retries_on_429(monkeypatch):
    calls = {"count": 0}

    def fake_get(_self, _url):
        calls["count"] += 1
        if calls["count"] == 1:
            return DummyResponse(429, headers={"Retry-After": "0"})
        return DummyResponse(
            200,
            payload={
                "data": {
                    "mal_id": 1,
                    "title": "Test Anime",
                    "genres": [{"name": "Action"}],
                    "episodes": 12,
                    "score": 8.4,
                    "members": 12345,
                    "status": "Finished Airing",
                    "images": {"jpg": {"image_url": "https://example.com/image.jpg"}},
                    "synopsis": "Test synopsis",
                }
            },
        )

    monkeypatch.setattr(httpx.Client, "get", fake_get)

    client = JikanAnimeClient()
    data = client.fetch_anime(1)
    assert data["title"] == "Test Anime"
    assert calls["count"] == 2
