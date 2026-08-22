from typing import List, Dict, Any

from agents.state import AgentState
from services.logger import log_info, log_error


def rank_resources(state: AgentState) -> AgentState:
    resources = state.get("evaluated_resources", [])

    log_info(
        f"Resource ranking started | resources_count={len(resources)}"
    )

    try:
        ranked_resources: List[Dict[str, Any]] = sorted(
            resources,
            key=lambda item: item.get("overall_score", 0.0),
            reverse=True
        )

        for index, resource in enumerate(ranked_resources, start=1):
            resource["rank"] = index

        log_info(
            f"Resource ranking completed | ranked_count={len(ranked_resources)}"
        )

        return {
            **state,
            "ranked_resources": ranked_resources,
        }

    except Exception as e:
        log_error(
            f"Resource ranking failed | error={e}"
        )
        raise