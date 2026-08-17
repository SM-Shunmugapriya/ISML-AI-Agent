from typing import Any


_cache = {}


def get_cached(key: str) -> Any:
    return _cache.get(key)


def set_cached(key: str, value: Any) -> None:
    _cache[key] = value


def clear_cache() -> None:
    _cache.clear()