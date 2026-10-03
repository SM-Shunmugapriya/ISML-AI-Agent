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
    workflow_run_id = state.get("workflow_run_id")

    log_info(
        f"Resource categorization started | "
        f"resources_count={len(resources)} | "
        f"workflow_run_id={workflow_run_id}"
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

            # Pass workflow_run_id only when available.
            # This keeps existing unit-test mocks compatible.
            if workflow_run_id:
                category = categorize_resource(
                    resource,
                    workflow_run_id=workflow_run_id,
                )
            else:
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
                f"category={category} | "
                f"workflow_run_id={workflow_run_id}"
            )

        log_info(
            f"Resource categorization completed | "
            f"categorized_count={len(categorized_resources)} | "
            f"workflow_run_id={workflow_run_id}"
        )

        return {
            **state,
            "categorized_resources": categorized_resources,
        }

    except Exception as e:
        log_error(
            f"Resource categorization failed | "
            f"workflow_run_id={workflow_run_id} | "
            f"error={e}"
        )
        raise