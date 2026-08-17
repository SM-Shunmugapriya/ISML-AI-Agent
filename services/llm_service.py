from services.deepseek_service import ask_deepseek
from services.gemini_service import ask_gemini
from services.logger import log_info, log_warning, log_error
from services.cache import get_cached, set_cached

import hashlib
import time


MAX_RETRIES = 3
RETRY_DELAY = 2


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

    for attempt in range(1, MAX_RETRIES + 1):

        try:
            start_time = time.perf_counter()

            if provider == "deepseek":
                response = ask_deepseek(prompt)

            elif provider == "gemini":
                response = ask_gemini(prompt)

            else:
                raise ValueError(
                    f"Unsupported LLM provider: {provider}"
                )

            elapsed_time = time.perf_counter() - start_time

            set_cached(cache_key, response)

            log_info(
                f"LLM request successful | "
                f"provider={provider} | "
                f"attempt={attempt} | "
                f"response_time={elapsed_time:.2f}s"
            )

            log_info(
                f"LLM response cached | provider={provider}"
            )

            return response

        except Exception as e:

            log_warning(
                f"LLM request failed | "
                f"provider={provider} | "
                f"attempt={attempt}/{MAX_RETRIES} | "
                f"error={e}"
            )

            if attempt < MAX_RETRIES:

                log_info(
                    f"Retrying LLM request | "
                    f"next_attempt={attempt + 1}"
                )

                time.sleep(RETRY_DELAY)

            else:

                log_error(
                    f"LLM request failed after "
                    f"{MAX_RETRIES} attempts | "
                    f"provider={provider} | "
                    f"error={e}"
                )

                raise