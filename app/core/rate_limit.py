import threading
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status

from app.core.config import settings

try:
    import redis
except Exception:  # pragma: no cover
    redis = None


class InMemoryRateLimiter:
    def __init__(self):
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def check(self, key: str, limit: int, window_seconds: int) -> None:
        now = time.time()
        cutoff = now - window_seconds
        with self._lock:
            queue = self._hits[key]
            while queue and queue[0] <= cutoff:
                queue.popleft()

            if len(queue) >= limit:
                retry_after = int(max(1, window_seconds - (now - queue[0])))
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded",
                    headers={"Retry-After": str(retry_after)},
                )
            queue.append(now)


rate_limiter = InMemoryRateLimiter()
redis_client = None
if settings.REDIS_URL and redis is not None:
    try:
        redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
        redis_client.ping()
    except Exception:
        redis_client = None


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def limit_requests(scope: str, limit_per_minute: int):
    def dependency(request: Request):
        ip = _client_ip(request)
        current_minute = int(time.time() // 60)
        key = f"{scope}:{ip}:{current_minute}"

        if redis_client is not None:
            count = redis_client.incr(key)
            if count == 1:
                redis_client.expire(key, 60)
            if count > limit_per_minute:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded",
                    headers={"Retry-After": "60"},
                )
            return

        local_key = f"{scope}:{ip}"
        rate_limiter.check(local_key, limit_per_minute, 60)

    return dependency
