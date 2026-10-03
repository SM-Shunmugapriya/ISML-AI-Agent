import hashlib
import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class CacheEntry:
    value: str
    created_at: float


class LLMCache:
    """
    In-memory cache for repeated LLM requests.
    """

    def __init__(self, ttl_seconds: int = 3600) -> None:
        self.ttl_seconds = ttl_seconds
        self._cache: dict[str, CacheEntry] = {}
        self.hits = 0
        self.misses = 0

    def _make_key(
        self,
        provider: str,
        model: str,
        prompt: str,
    ) -> str:
        raw_key = f"{provider}:{model}:{prompt}"
        return hashlib.sha256(
            raw_key.encode("utf-8")
        ).hexdigest()

    def get(
        self,
        provider: str,
        model: str,
        prompt: str,
    ) -> Optional[str]:
        key = self._make_key(provider, model, prompt)
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
        self.hits = 0
        self.misses = 0

    def get_stats(self) -> dict:
        return {
            "hits": self.hits,
            "misses": self.misses,
            "total_requests": self.total_requests,
            "hit_rate": round(self.hit_rate, 4),
        }


llm_cache = LLMCache()