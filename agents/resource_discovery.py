from typing import List, Dict, Any

from agents.state import AgentState
from tools.web_search import web_search
from tools.youtube_search import youtube_search
from tools.pdf_search import pdf_search
from services.logger import log_info, log_error


def discover_resources(state: AgentState) -> AgentState:
    search_queries = state.get("search_queries", [])

    log_info(
        f"Resource discovery started | queries_count={len(search_queries)}"
    )

    resources: List[Dict[str, Any]] = []

    try:
        for query in search_queries:
            log_info(f"Searching resources | query={query}")

            # Web resources
            web_result = web_search(query, max_results=5)

            for item in web_result.get("results", []):
                resources.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "content": item.get("content", ""),
                    "resource_type": "web",
                    "score": item.get("score", 0.0),
                })

            # YouTube resources
            youtube_result = youtube_search(
                query,
                max_results=5
            )

            for item in youtube_result.get("results", []):
                resources.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "content": "",
                    "resource_type": "youtube",
                    "channel": item.get("channel", ""),
                    "duration": item.get("duration", ""),
                    "views": item.get("views", ""),
                })

            # PDF resources
            pdf_result = pdf_search(
                query,
                max_results=5
            )

            for item in pdf_result.get("results", []):
                resources.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "content": item.get("content", ""),
                    "resource_type": "pdf",
                    "score": item.get("score", 0.0),
                })

        log_info(
            f"Resource discovery completed | resources_count={len(resources)}"
        )

        return {
            **state,
            "search_results": resources,
            "resources": resources,
        }

    except Exception as e:
        log_error(
            f"Resource discovery failed | error={e}"
        )
        raise