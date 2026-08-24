import os
import time

from dotenv import load_dotenv
from tavily import TavilyClient

from services.logger import log_info, log_warning, log_error


load_dotenv()


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
    retries: int = 2
):
    """
    Search the web for educational resources.

    If the Tavily API key is missing, the search is
    skipped and an empty result is returned.

    Retries the Tavily request if a temporary
    connection or timeout error occurs.
    """

    tavily_client = get_tavily_client()

    # Graceful fallback when API key is missing
    if tavily_client is None:
        return {
            "query": query,
            "results": []
        }

    for attempt in range(1, retries + 2):

        try:
            log_info(
                f"Tavily search started | "
                f"query={query} | attempt={attempt}"
            )

            response = tavily_client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results,
                include_answer=True,
            )

            log_info(
                f"Tavily search completed | query={query}"
            )

            return response

        except Exception as e:

            log_warning(
                f"Tavily search failed | "
                f"query={query} | "
                f"attempt={attempt} | "
                f"error={e}"
            )

            if attempt <= retries:
                wait_time = attempt * 2

                log_info(
                    f"Retrying Tavily search | "
                    f"wait={wait_time}s"
                )

                time.sleep(wait_time)

            else:
                log_error(
                    f"Tavily search failed after retries | "
                    f"query={query}"
                )

                # Don't crash the entire workflow.
                return {
                    "query": query,
                    "results": []
                }