from typing import List, Dict, Any

from agents.state import AgentState
from services.categorization_service import categorize_resource
from services.logger import log_info, log_error


def categorize_resources(state: AgentState) -> AgentState:
    """
    Categorize ranked educational resources based on
    their pedagogical learning purpose.
    """

    resources = state.get("ranked_resources", [])

    log_info(
        f"Resource categorization started | "
        f"resources_count={len(resources)}"
    )

    categorized_resources: List[Dict[str, Any]] = []

    try:
        if not resources:
            log_info(
                "Resource categorization completed | "
                "no resources available"
            )

            return {
                **state,
                "categorized_resources": [],
            }

        for resource in resources:
            category = categorize_resource(resource)

            categorized_resource = {
                **resource,
                "category": category,
            }

            categorized_resources.append(
                categorized_resource
            )

            log_info(
                f"Resource categorized | "
                f"title={resource.get('title', '')} | "
                f"category={category}"
            )

        log_info(
            f"Resource categorization completed | "
            f"categorized_count={len(categorized_resources)}"
        )

        return {
            **state,
            "categorized_resources": categorized_resources,
        }

    except Exception as e:
        log_error(
            f"Resource categorization failed | error={e}"
        )
        raise