from services.deepseek_service import (
    ask_deepseek,
    get_last_usage as get_deepseek_usage,
)
from services.gemini_service import (
    ask_gemini,
    get_last_usage as get_gemini_usage,
)
from services.logger import log_info
from services.model_router import model_router
from services.llm_cache import llm_cache
from services.cost_tracker import cost_tracker
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


# Backward compatibility for existing tests/callers.
def get_cached(prompt: str, provider: str):
    model = (
        "gemini-3.6-flash"
        if provider == "gemini"
        else "deepseek-chat"
    )

    return llm_cache.get(
        provider=provider,
        model=model,
        prompt=prompt,
    )


def ask_llm(
    prompt: str,
    provider: str | None = None,
    workflow_run_id: str | None = None,
) -> dict:

    # ENH-007: Automatically select the cheapest
    # capable model when provider is not explicitly given.
    if provider is None:
        route = model_router.route(prompt)
        provider = route.provider

        log_info(
            f"Model routing | "
            f"provider={route.provider} | "
            f"model={route.model} | "
            f"reason={route.reason}"
        )

    # ENH-007: LLM cache
    model = (
        "gemini-3.6-flash"
        if provider == "gemini"
        else "deepseek-chat"
    )

    cached_response = get_cached(
        prompt=prompt,
        provider=provider,
    )

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
        get_usage = get_deepseek_usage

    elif provider == "gemini":
        api_call = ask_gemini
        get_usage = get_gemini_usage

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

    # ENH-007: Read actual token usage from provider.
    usage = get_usage()

    input_tokens = usage.get("input_tokens", 0)
    output_tokens = usage.get("output_tokens", 0)

    # ENH-007: Track actual LLM cost per workflow run.
    if workflow_run_id is not None:
        record = cost_tracker.record(
            workflow_run_id=workflow_run_id,
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )

        log_info(
            f"LLM cost tracked | "
            f"workflow_run_id={workflow_run_id} | "
            f"provider={provider} | "
            f"model={model} | "
            f"input_tokens={input_tokens} | "
            f"output_tokens={output_tokens} | "
            f"cost={record.cost}"
        )

    # ENH-007: Store response in LLM cache.
    llm_cache.set(
        provider=provider,
        model=model,
        prompt=prompt,
        value=response,
    )

    log_info(
        f"LLM response cached | provider={provider}"
    )

    return response