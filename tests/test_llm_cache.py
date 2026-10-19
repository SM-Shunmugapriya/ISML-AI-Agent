from services.llm_cache import LLMCache


def test_cache_miss_then_hit():
    cache = LLMCache()

    assert cache.get(
        "gemini",
        "gemini-3.6-flash",
        "hello",
    ) is None

    cache.set(
        "gemini",
        "gemini-3.6-flash",
        "hello",
        "cached response",
    )

    assert cache.get(
        "gemini",
        "gemini-3.6-flash",
        "hello",
    ) == "cached response"


def test_cache_hit_rate():
    cache = LLMCache()

    cache.set(
        "gemini",
        "gemini-3.6-flash",
        "hello",
        "cached response",
    )

    cache.get("gemini", "gemini-3.6-flash", "hello")
    cache.get("gemini", "gemini-3.6-flash", "hello")

    stats = cache.get_stats()

    assert stats["hits"] == 2
    assert stats["misses"] == 0
    assert stats["hit_rate"] == 1.0


def test_cache_clear():
    cache = LLMCache()

    cache.set(
        "gemini",
        "gemini-3.6-flash",
        "hello",
        "cached response",
    )

    cache.clear()

    assert cache.get(
        "gemini",
        "gemini-3.6-flash",
        "hello",
    ) is None
def test_cache_ttl_expiration(monkeypatch):
    import services.llm_cache as cache_module

    current_time = [100.0]
    monkeypatch.setattr(cache_module.time, "time", lambda: current_time[0])

    cache = LLMCache(ttl_seconds=5)
    cache.set("gemini", "model", "hello", "cached response")

    assert cache.get("gemini", "model", "hello") == "cached response"

    current_time[0] = 106.0
    assert cache.get("gemini", "model", "hello") is None


def test_cache_metrics_after_miss_and_hit():
    cache = LLMCache()

    assert cache.get("gemini", "model", "hello") is None
    cache.set("gemini", "model", "hello", "cached response")
    assert cache.get("gemini", "model", "hello") == "cached response"

    stats = cache.get_stats()
    assert stats["hits"] == 1
    assert stats["misses"] == 1
    assert stats["total_requests"] == 2
    assert stats["hit_rate"] == 0.5
    assert stats["backend"] == "memory"


def test_redis_unavailable_falls_back_to_memory(monkeypatch):
    cache = LLMCache()
    monkeypatch.setattr(cache, "_redis", None)

    cache.set("gemini", "model", "hello", "cached response")

    assert cache.get("gemini", "model", "hello") == "cached response"
    assert cache.get_stats()["backend"] == "memory"
