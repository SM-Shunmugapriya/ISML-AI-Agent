import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY is not configured in .env")

tavily_client = TavilyClient(api_key=TAVILY_API_KEY)


def web_search(query: str, max_results: int = 5):
    """
    Search the web for educational resources.
    """

    response = tavily_client.search(
        query=query,
        search_depth="advanced",
        max_results=max_results,
        include_answer=True,
    )

    return response