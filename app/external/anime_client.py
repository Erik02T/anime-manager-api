"""Camada External Client (Jikan).

Responsabilidade:
- Consumir API externa de anime (Jikan).
- Aplicar retry/backoff, cache e mapeamento para formato interno.

Dependências usadas:
- httpx para chamadas HTTP
- cache_store para reduzir latência/custo de requisição
- settings para timeout/retry/base URL
"""

import httpx
import time
from datetime import datetime

from app.core.cache import cache_store
from app.core.config import settings


class JikanAnimeClient:
    def __init__(self):
        # Configuração centralizada via variáveis de ambiente.
        self.base_url = settings.JIKAN_BASE_URL.rstrip("/")
        self.timeout = settings.EXTERNAL_API_TIMEOUT_SECONDS
        self.cache_ttl = settings.EXTERNAL_CACHE_TTL_SECONDS
        self.max_retries = settings.EXTERNAL_API_MAX_RETRIES
        self.backoff_seconds = settings.EXTERNAL_API_BACKOFF_SECONDS

    def fetch_anime(self, mal_id: int) -> dict:
        # Detalhes completos de um anime por MAL ID (rota /anime/{id}/full).
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

    def fetch_top_anime(self, limit: int = 25) -> list[dict]:
        # Ranking de popularidade geral para vitrine/recomendação.
        cache_key = f"external:jikan:top:{limit}"
        cached = cache_store.get(cache_key)
        if cached is not None:
            return cached

        payload = self._get_with_retry(f"{self.base_url}/top/anime?limit={max(1, min(limit, 50))}&sfw=true")
        mapped = [self._map_catalog_item(item) for item in (payload.get("data") or [])]
        cache_store.set(cache_key, mapped, ttl_seconds=self.cache_ttl)
        return mapped

    def fetch_current_season(self, limit: int = 25) -> list[dict]:
        # Temporada atual para captar títulos em destaque e lançamentos correntes.
        cache_key = f"external:jikan:season-now:{limit}"
        cached = cache_store.get(cache_key)
        if cached is not None:
            return cached

        payload = self._get_with_retry(f"{self.base_url}/seasons/now?limit={max(1, min(limit, 50))}&sfw=true")
        mapped = [self._map_catalog_item(item) for item in (payload.get("data") or [])]
        cache_store.set(cache_key, mapped, ttl_seconds=self.cache_ttl)
        return mapped

    def fetch_upcoming(self, limit: int = 20) -> list[dict]:
        # Próximos lançamentos para feed de notícias.
        cache_key = f"external:jikan:upcoming:{limit}"
        cached = cache_store.get(cache_key)
        if cached is not None:
            return cached

        payload = self._get_with_retry(f"{self.base_url}/seasons/upcoming?limit={max(1, min(limit, 50))}&sfw=true")
        mapped = [self._map_catalog_item(item) for item in (payload.get("data") or [])]
        cache_store.set(cache_key, mapped, ttl_seconds=self.cache_ttl)
        return mapped

    def fetch_season_catalog(self, year: int, season: str, pages: int = 1) -> list[dict]:
        # Ingestão por temporada/ano para importação de catálogos históricos.
        safe_pages = max(1, min(pages, 10))
        cache_key = f"external:jikan:season:{year}:{season}:{safe_pages}"
        cached = cache_store.get(cache_key)
        if cached is not None:
            return cached

        items: list[dict] = []
        normalized_season = season.lower().strip()
        for page in range(1, safe_pages + 1):
            payload = self._get_with_retry(
                f"{self.base_url}/seasons/{year}/{normalized_season}?page={page}&sfw=true"
            )
            page_items = [self._map_catalog_item(item) for item in (payload.get("data") or [])]
            items.extend(page_items)
            pagination = payload.get("pagination") or {}
            if not pagination.get("has_next_page", False):
                break

        cache_store.set(cache_key, items, ttl_seconds=self.cache_ttl)
        return items

    def _map_catalog_item(self, data: dict) -> dict:
        return {
            "mal_id": data.get("mal_id"),
            "title": data.get("title") or "Unknown title",
            "genre": ", ".join([g.get("name") for g in (data.get("genres") or []) if g.get("name")]) or "Unknown",
            "episodes": data.get("episodes") or 0,
            "external_score": self._normalize_score(data.get("score")),
            "members": data.get("members"),
            "external_status": data.get("status"),
            "image_url": ((data.get("images") or {}).get("jpg") or {}).get("image_url"),
            "synopsis": data.get("synopsis"),
            "aired_from": self._parse_datetime((data.get("aired") or {}).get("from")),
            "url": data.get("url"),
        }

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

    @staticmethod
    def _parse_datetime(value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            # Jikan usually sends ISO with Z suffix.
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except Exception:
            return None
