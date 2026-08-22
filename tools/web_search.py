import os
import time

from dotenv import load_dotenv
from tavily import TavilyClient

from services.logger import log_info, log_warning, log_error


load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY is not configured in .env")

tavily_client = TavilyClient(
    api_key=TAVILY_API_KEY
)


def web_search(
    query: str,
    max_results: int = 5,
    retries: int = 2
):
    """
    Search the web for educational resources.

    Retries the Tavily request if a temporary
    connection or timeout error occurs.
    """

    for attempt in range(1, retries + 2):

        try:
            log_info(
                f"Tavily search started | query={query} | attempt={attempt}"
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