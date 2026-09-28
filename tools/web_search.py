import os

from dotenv import load_dotenv
from tavily import TavilyClient

from services.logger import log_info, log_warning
from services.resilience_service import (
    retry_with_backoff,
    CircuitBreaker,
)


load_dotenv()


TAVILY_CIRCUIT_BREAKER = CircuitBreaker(
    failure_threshold=5
)


def get_tavily_client():
    """
    Lazily initialize the Tavily client.

    Returns None when the API key is missing so that
    the application can continue running safely.
    """
    tavily_api_key = os.getenv("TAVILY_API_KEY")

    if not tavily_api_key:
        log_warning(
            "TAVILY_API_KEY is not configured. "
            "Tavily search will be skipped."
        )
        return None

    return TavilyClient(api_key=tavily_api_key)


def web_search(
    query: str,
    max_results: int = 5,
    retries: int = 3
):
    """
    Search the web for educational resources.

    Uses retry with exponential backoff and circuit
    breaker protection for Tavily API failures.

    If the Tavily API key is missing or the request
    fails after retries, an empty result is returned.
    """

    tavily_client = get_tavily_client()

    # Graceful fallback when API key is missing
    if tavily_client is None:
        return {
            "query": query,
            "results": []
        }

    log_info(
        f"Tavily search started | query={query}"
    )

    def tavily_request():
        return tavily_client.search(
            query=query,
            search_depth="advanced",
            max_results=max_results,
            include_answer=True,
        )

    try:
        resilient_search = retry_with_backoff(
            max_retries=retries,
            backoff_factor=1,
            timeout=30,
            circuit_breaker=TAVILY_CIRCUIT_BREAKER,
        )(tavily_request)

        response = resilient_search()

        log_info(
            f"Tavily search completed | query={query}"
        )

        return response

    except Exception as e:
        log_warning(
            f"Tavily search unavailable | "
            f"query={query} | "
            f"error={e}"
        )

        # Controlled fallback
        return {
            "query": query,
            "results": []
        }