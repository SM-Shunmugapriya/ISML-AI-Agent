import pytest

from services.llm_cache import LLMCache


@pytest.fixture
def memory_cache(monkeypatch):
    cache = LLMCache()
    monkeypatch.setattr(cache, "_redis", None)
    return cache


def test_cache_miss_then_hit(memory_cache):
    cache = memory_cache

    assert cache.get("gemini", "gemini-3.6-flash", "hello") is None
    cache.set("gemini", "gemini-3.6-flash", "hello", "cached response")
    assert cache.get("gemini", "gemini-3.6-flash", "hello") == "cached response"


def test_cache_hit_rate(memory_cache):
    cache = memory_cache

    cache.set("gemini", "gemini-3.6-flash", "hello", "cached response")
    cache.get("gemini", "gemini-3.6-flash", "hello")
    cache.get("gemini", "gemini-3.6-flash", "hello")

    stats = cache.get_stats()
    assert stats["hits"] == 2
    assert stats["misses"] == 0
    assert stats["hit_rate"] == 1.0


def test_cache_clear(memory_cache):
    cache = memory_cache

    cache.set("gemini", "gemini-3.6-flash", "hello", "cached response")
    cache.clear()

    assert cache.get("gemini", "gemini-3.6-flash", "hello") is None


def test_cache_ttl_expiration(monkeypatch, memory_cache):
    import services.llm_cache as cache_module

    current_time = [100.0]
    monkeypatch.setattr(cache_module.time, "time", lambda: current_time[0])

    cache = memory_cache
    cache.ttl_seconds = 5
    cache.set("gemini", "model", "hello", "cached response")

    assert cache.get("gemini", "model", "hello") == "cached response"

    current_time[0] = 106.0
    assert cache.get("gemini", "model", "hello") is None


def test_cache_metrics_after_miss_and_hit(memory_cache):
    cache = memory_cache

    assert cache.get("gemini", "model", "hello") is None
    cache.set("gemini", "model", "hello", "cached response")
    assert cache.get("gemini", "model", "hello") == "cached response"

    stats = cache.get_stats()
    assert stats["hits"] == 1
    assert stats["misses"] == 1
    assert stats["total_requests"] == 2
    assert stats["hit_rate"] == 0.5
    assert stats["backend"] == "memory"


def test_redis_unavailable_falls_back_to_memory(monkeypatch, memory_cache):
    cache = memory_cache

    cache.set("gemini", "model", "hello", "cached response")
    assert cache.get("gemini", "model", "hello") == "cached response"
    assert cache.get_stats()["backend"] == "memory"


def test_redis_integration_when_configured():
    import os
    from dotenv import load_dotenv

    load_dotenv()

    if not os.getenv("REDIS_URL"):
        pytest.skip("REDIS_URL is not configured for this test")

    cache = LLMCache(ttl_seconds=60)
    if cache.get_stats()["backend"] != "redis":
        pytest.skip("Redis server is unavailable")

    prompt = "pytest-redis-integration-enh013"
    cache.set("test", "test-model", prompt, "redis integration ok")

    assert cache.get("test", "test-model", prompt) == "redis integration ok"
