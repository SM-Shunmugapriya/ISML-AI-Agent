from agents.state import AgentState
from services.dedup_service import deduplicate_resources
from services.logger import log_info, log_error


def deduplicate_resources_node(state: AgentState) -> AgentState:
    """
    Deduplicate validated resources using normalized URLs.
    """

    resources = state.get("validated_resources", [])

    log_info(
        f"Deduplication started | resources_count={len(resources)}"
    )

    try:
        unique_resources = deduplicate_resources(resources)

        log_info(
            f"Deduplication completed | "
            f"unique_count={len(unique_resources)}"
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