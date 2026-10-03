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