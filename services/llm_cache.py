import hashlib
import json
import os
import time
from dataclasses import dataclass
from typing import Optional

try:
    import redis
except ImportError:
    redis = None


@dataclass
class CacheEntry:
    value: str
    created_at: float


class LLMCache:
    """TTL cache with optional Redis backend and in-memory fallback."""

    def __init__(self, ttl_seconds: int = 3600) -> None:
        self.ttl_seconds = ttl_seconds
        self._cache: dict[str, CacheEntry] = {}
        self.hits = 0
        self.misses = 0
        self._redis = None

        redis_url = os.getenv("REDIS_URL")
        if redis is not None and redis_url:
            try:
                client = redis.Redis.from_url(
                    redis_url,
                    socket_connect_timeout=1,
                    socket_timeout=1,
                    decode_responses=True,
                )
                client.ping()
                self._redis = client
            except Exception:
                self._redis = None

    def _make_key(self, provider: str, model: str, prompt: str) -> str:
        raw_key = f"{provider}:{model}:{prompt}"
        digest = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
        return f"isml:llm_cache:{digest}"

    def get(
        self,
        provider: str,
        model: str,
        prompt: str,
    ) -> Optional[str]:
        key = self._make_key(provider, model, prompt)

        if self._redis is not None:
            try:
                raw = self._redis.get(key)
                if raw is None:
                    self.misses += 1
                    return None
                payload = json.loads(raw)
                self.hits += 1
                return payload["value"]
            except Exception:
                self._redis = None

        entry = self._cache.get(key)
        if entry is None:
            self.misses += 1
            return None

        if time.time() - entry.created_at > self.ttl_seconds:
            del self._cache[key]
            self.misses += 1
            return None

        self.hits += 1
        return entry.value

    def set(
        self,
        provider: str,
        model: str,
        prompt: str,
        value: str,
    ) -> None:
        key = self._make_key(provider, model, prompt)

        if self._redis is not None:
            try:
                payload = json.dumps({
                    "value": value,
                    "created_at": time.time(),
                })
                self._redis.set(key, payload, ex=self.ttl_seconds)
                return
            except Exception:
                self._redis = None

        self._cache[key] = CacheEntry(
            value=value,
            created_at=time.time(),
        )

    @property
    def total_requests(self) -> int:
        return self.hits + self.misses

    @property
    def hit_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return self.hits / self.total_requests

    def clear(self) -> None:
        self._cache.clear()
        if self._redis is not None:
            try:
                keys = list(self._redis.scan_iter(match="isml:llm_cache:*"))
                if keys:
                    self._redis.delete(*keys)
            except Exception:
                self._redis = None
        self.hits = 0
        self.misses = 0

    def get_stats(self) -> dict:
        return {
            "hits": self.hits,
            "misses": self.misses,
            "total_requests": self.total_requests,
            "hit_rate": round(self.hit_rate, 4),
            "backend": "redis" if self._redis is not None else "memory",
        }


llm_cache = LLMCache()
