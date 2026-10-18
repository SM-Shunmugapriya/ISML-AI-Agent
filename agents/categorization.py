
from typing import List, Dict, Any

from agents.state import AgentState
from services.categorization_service import categorize_resource
from app.categorization.categorization_service import (
    categorize_resource as calculate_category_confidence,
)
from services.logger import log_info, log_error


def categorize_resources(state: AgentState) -> AgentState:
    """
    Categorize ranked educational resources and attach a
    heuristic confidence score for ENH-012 human review.
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
            # Preserve the existing LLM categorization behavior.
            # Pass workflow_run_id only when available so existing
            # unit-test mocks remain compatible.
            if workflow_run_id:
                category = categorize_resource(
                    resource,
                    workflow_run_id=workflow_run_id,
                )
            else:
                category = categorize_resource(resource)

            # Calculate a separate keyword-based heuristic score.
            confidence_result = calculate_category_confidence(
                metadata={
                    "title": resource.get("title", ""),
                    "resource_type": resource.get(
                        "resource_type",
                        resource.get("type", ""),
                    ),
                    "source": resource.get("source", ""),
                    "description": resource.get("description", ""),
                    "summary": resource.get("summary", ""),
                },
                content_snippet=resource.get("content", ""),
            )

            heuristic_category = confidence_result["category"]
            heuristic_confidence = float(
                confidence_result["confidence"]
            )

            # A category mismatch requires human review.
            # This is a heuristic score, not calibrated AI confidence.
            review_confidence = (
                heuristic_confidence
                if category == heuristic_category
                else 0.0
            )

            categorized_resource = {
                **resource,
                "category": category,
                "review_confidence": review_confidence,
            }

            categorized_resources.append(categorized_resource)

            log_info(
                f"Resource categorized | "
                f"title={resource.get('title', '')} | "
                f"category={category} | "
                f"review_confidence={review_confidence} | "
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
