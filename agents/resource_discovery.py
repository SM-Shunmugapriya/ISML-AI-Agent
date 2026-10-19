
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Tuple

from agents.state import AgentState
from tools.web_search import web_search
from tools.youtube_search import youtube_search
from tools.pdf_search import pdf_search
from tools.audio_search import audio_search
from services.logger import log_info, log_error


def discover_resources(state: AgentState) -> AgentState:
    search_queries = list(dict.fromkeys(state.get("search_queries", [])))
    search_tools = state.get("search_tools", ["web"])

    log_info(
        f"Resource discovery started | "
        f"queries_count={len(search_queries)} | "
        f"selected_tools={search_tools}"
    )

    resources: List[Dict[str, Any]] = []

    search_functions = {
        "web": web_search,
        "youtube": youtube_search,
        "pdf": pdf_search,
        "audio": audio_search,
    }

    # Create tasks in a stable order while removing duplicate queries.
    tasks: List[Tuple[str, str]] = [
        (query, tool_name)
        for query in search_queries
        for tool_name in search_functions
        if tool_name in search_tools
    ]

    def run_search(task: Tuple[str, str]):
        query, tool_name = task

        log_info(
            f"Searching resources | "
            f"query={query} | tool={tool_name}"
        )

        try:
            result = search_functions[tool_name](
                query,
                max_results=5,
            )
            return query, tool_name, result, None
        except Exception as exc:
            return query, tool_name, {}, exc

    try:
        if tasks:
            with ThreadPoolExecutor(
                max_workers=min(8, len(tasks))
            ) as executor:
                search_outputs = list(executor.map(run_search, tasks))
        else:
            search_outputs = []

        for query, tool_name, result, error in search_outputs:
            if error is not None:
                log_error(
                    f"Resource search failed | "
                    f"query={query} | tool={tool_name} | error={error}"
                )
                continue

            for item in result.get("results", []):
                if tool_name == "web":
                    resources.append({
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "content": item.get("content", ""),
                        "resource_type": "web",
                        "score": item.get("score", 0.0),
                    })

                elif tool_name == "youtube":
                    resources.append({
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "content": "",
                        "resource_type": "youtube",
                        "channel": item.get("channel", ""),
                        "duration": item.get("duration", ""),
                        "views": item.get("views", ""),
                    })

                elif tool_name == "pdf":
                    resources.append({
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "content": item.get("content", ""),
                        "resource_type": "pdf",
                        "score": item.get("score", 0.0),
                    })

                elif tool_name == "audio":
                    resources.append({
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "content": item.get("description", ""),
                        "resource_type": "audio",
                    })

        log_info(
            f"Resource discovery completed | "
            f"resources_count={len(resources)}"
        )

        return {
            **state,
            "search_results": resources,
            "resources": resources,
        }

    except Exception as exc:
        log_error(
            f"Resource discovery failed | error={exc}"
        )
        raise
