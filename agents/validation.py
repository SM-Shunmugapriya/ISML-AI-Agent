from typing import List, Dict, Any

from agents.state import AgentState
from services.logger import log_info, log_error


def validate_resources(state: AgentState) -> AgentState:
    metadata = state.get("metadata", [])

    log_info(
        f"Resource validation started | resources_count={len(metadata)}"
    )

    validated_resources: List[Dict[str, Any]] = []

    try:
        for resource in metadata:
            title = resource.get("title", "").strip()
            url = resource.get("url", "").strip()

            if not title or not url:
                continue

            if not url.startswith(("http://", "https://")):
                continue

            validated_resources.append(resource)

        log_info(
            f"Resource validation completed | valid_count={len(validated_resources)}"
        )

        return {
            **state,
            "validated_resources": validated_resources,
        }

    except Exception as e:
        log_error(
            f"Resource validation failed | error={e}"
        )
        raise