"""
Arquivo: backend/app/core/cache.py
Camada: Module
Objetivo: Define responsabilidades deste modulo e sua funcao no sistema.
Dependencias: FastAPI/SQLAlchemy/Pydantic e utilitarios internos conforme necessario.
"""

import threading
import time
import json

from app.core.config import settings

try:
    import redis
except Exception:  # pragma: no cover
    redis = None


class CacheStore:
    def __init__(self):
        self._data: dict[str, tuple[float, object]] = {}
        self._lock = threading.Lock()
        self._redis_client = None
        if settings.REDIS_URL and redis is not None:
            try:
                self._redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=False)
                self._redis_client.ping()
            except Exception:
                self._redis_client = None

    def get(self, key: str):
        if self._redis_client is not None:
            raw = self._redis_client.get(key)
            if raw is None:
                return None
            try:
                return json.loads(raw.decode("utf-8"))
            except Exception:
                self._redis_client.delete(key)
                return None

        with self._lock:
            entry = self._data.get(key)
            if not entry:
                return None
            expires_at, value = entry
            if expires_at < time.time():
                self._data.pop(key, None)
                return None
            return value

    def set(self, key: str, value, ttl_seconds: int = 60):
        if self._redis_client is not None:
            self._redis_client.setex(key, ttl_seconds, json.dumps(value))
            return

        with self._lock:
            self._data[key] = (time.time() + ttl_seconds, value)

    def invalidate(self, key: str):
        if self._redis_client is not None:
            self._redis_client.delete(key)
            return

        with self._lock:
            self._data.pop(key, None)

    def invalidate_prefix(self, prefix: str):
        if self._redis_client is not None:
            keys = self._redis_client.keys(f"{prefix}*")
            if keys:
                self._redis_client.delete(*keys)
            return

        with self._lock:
            keys = [k for k in self._data if k.startswith(prefix)]
            for key in keys:
                self._data.pop(key, None)


cache_store = CacheStore()



