from typing import List, Dict, Any

from agents.state import AgentState
from services.logger import log_info, log_error


def rank_resources(state: AgentState) -> AgentState:
    """
    Rank evaluated educational resources based on their
    composite quality score.

    The resources are expected to already contain
    evaluation results from the evaluation stage.
    """

    resources = state.get("evaluated_resources", [])

    log_info(
        f"Resource ranking started | resources_count={len(resources)}"
    )

    try:
        # Handle empty resource list
        if not resources:
            log_info(
                "Resource ranking completed | no resources available"
            )

            return {
                **state,
                "ranked_resources": [],
            }

        # Rank resources by composite quality score
        # from highest to lowest.
        ranked_resources: List[Dict[str, Any]] = sorted(
            resources,
            key=lambda item: item.get("overall_score", 0.0),
            reverse=True,
        )

        # Assign rank and ranking explanation
        for index, resource in enumerate(
            ranked_resources,
            start=1,
        ):
            score = resource.get("overall_score", 0.0)

            resource["rank"] = index

            resource["ranking_explanation"] = (
                f"Ranked #{index} based on a composite "
                f"quality score of {score}."
            )

        log_info(
            f"Resource ranking completed | "
            f"ranked_count={len(ranked_resources)}"
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