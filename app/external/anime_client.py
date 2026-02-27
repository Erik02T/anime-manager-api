import httpx
import time

from app.core.cache import cache_store
from app.core.config import settings


class JikanAnimeClient:
    def __init__(self):
        self.base_url = settings.JIKAN_BASE_URL.rstrip("/")
        self.timeout = settings.EXTERNAL_API_TIMEOUT_SECONDS
        self.cache_ttl = settings.EXTERNAL_CACHE_TTL_SECONDS
        self.max_retries = settings.EXTERNAL_API_MAX_RETRIES
        self.backoff_seconds = settings.EXTERNAL_API_BACKOFF_SECONDS

    def fetch_anime(self, mal_id: int) -> dict:
        cache_key = f"external:jikan:anime:{mal_id}"
        cached = cache_store.get(cache_key)
        if cached is not None:
            return cached

        url = f"{self.base_url}/anime/{mal_id}/full"
        payload = self._get_with_retry(url)

        data = payload.get("data")
        if not data:
            raise ValueError("External anime data not found")

        mapped = {
            "mal_id": data.get("mal_id"),
            "title": data.get("title") or "Unknown title",
            "genre": ", ".join([g.get("name") for g in (data.get("genres") or []) if g.get("name")]) or "Unknown",
            "episodes": data.get("episodes") or 0,
            "external_score": self._normalize_score(data.get("score")),
            "members": data.get("members"),
            "external_status": data.get("status"),
            "image_url": ((data.get("images") or {}).get("jpg") or {}).get("image_url"),
            "synopsis": data.get("synopsis"),
        }
        cache_store.set(cache_key, mapped, ttl_seconds=self.cache_ttl)
        return mapped

    def _get_with_retry(self, url: str) -> dict:
        with httpx.Client(timeout=self.timeout) as client:
            attempt = 0
            while True:
                attempt += 1
                response = client.get(url)
                if response.status_code < 400:
                    return response.json()

                retryable = response.status_code == 429 or 500 <= response.status_code < 600
                if not retryable or attempt > self.max_retries:
                    response.raise_for_status()

                retry_after = response.headers.get("Retry-After")
                if retry_after and retry_after.isdigit():
                    sleep_seconds = int(retry_after)
                else:
                    sleep_seconds = self.backoff_seconds * (2 ** (attempt - 1))
                time.sleep(max(0, sleep_seconds))

    @staticmethod
    def _normalize_score(score: float | int | None) -> int | None:
        if score is None:
            return None
        try:
            normalized = round(float(score))
            if normalized < 0:
                return 0
            if normalized > 10:
                return 10
            return int(normalized)
        except Exception:
            return None
