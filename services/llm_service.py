from services.deepseek_service import ask_deepseek
from services.gemini_service import ask_gemini
from services.logger import log_info
from services.cache import get_cached, set_cached
from services.resilience_service import (
    retry_with_backoff,
    CircuitBreaker,
)

import hashlib


LLM_CIRCUIT_BREAKER = CircuitBreaker(
    failure_threshold=5
)


def create_cache_key(prompt: str, provider: str) -> str:
    data = f"{provider}:{prompt}"
    return hashlib.sha256(data.encode()).hexdigest()


def ask_llm(prompt: str, provider: str = "gemini") -> dict:
    cache_key = create_cache_key(prompt, provider)

    cached_response = get_cached(cache_key)

    if cached_response is not None:
        log_info(
            f"LLM cache hit | provider={provider}"
        )
        return cached_response

    log_info(
        f"LLM cache miss | provider={provider}"
    )

    log_info(
        f"LLM request started | provider={provider}"
    )

    if provider == "deepseek":
        api_call = ask_deepseek

    elif provider == "gemini":
        api_call = ask_gemini

    else:
        raise ValueError(
            f"Unsupported LLM provider: {provider}"
        )

    resilient_api_call = retry_with_backoff(
        max_retries=3,
        backoff_factor=1,
        timeout=30,
        circuit_breaker=LLM_CIRCUIT_BREAKER,
    )(api_call)

    response = resilient_api_call(prompt)

    set_cached(cache_key, response)

    log_info(
        f"LLM response cached | provider={provider}"
    )

    return response
