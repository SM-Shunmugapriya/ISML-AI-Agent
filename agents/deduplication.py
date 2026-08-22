from typing import List, Dict, Any

from agents.state import AgentState
from services.logger import log_info, log_error


def deduplicate_resources(state: AgentState) -> AgentState:
    resources = state.get("validated_resources", [])

    log_info(
        f"Deduplication started | resources_count={len(resources)}"
    )

    unique_resources: List[Dict[str, Any]] = []
    seen_urls = set()

    try:
        for resource in resources:
            url = resource.get("url", "").strip()

            if not url:
                continue

            if url in seen_urls:
                continue

            seen_urls.add(url)
            unique_resources.append(resource)

        log_info(
            f"Deduplication completed | unique_count={len(unique_resources)}"
        )

        return {
            **state,
            "unique_resources": unique_resources,
        }

    except Exception as e:
        log_error(
            f"Deduplication failed | error={e}"
        )
        raise