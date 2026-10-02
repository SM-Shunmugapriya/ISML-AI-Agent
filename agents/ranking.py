from typing import List, Dict, Any

from agents.state import AgentState
from services.ranking_explainer import RankingExplainer
from services.logger import log_info, log_error


ranking_explainer = RankingExplainer()

TOP_N_EXPLANATIONS = 5


def rank_resources(state: AgentState) -> AgentState:
    """
    Rank evaluated educational resources based on their
    composite quality score and generate explanations
    for the top-ranked resources.
    """

    resources = state.get("evaluated_resources", [])

    log_info(
        f"Resource ranking started | resources_count={len(resources)}"
    )

    try:
        if not resources:
            log_info(
                "Resource ranking completed | no resources available"
            )

            return {
                **state,
                "ranked_resources": [],
            }

        ranked_resources: List[Dict[str, Any]] = sorted(
            resources,
            key=lambda item: item.get("overall_score", 0.0),
            reverse=True,
        )

        for index, resource in enumerate(
            ranked_resources,
            start=1,
        ):
            resource["rank"] = index

            if index <= TOP_N_EXPLANATIONS:
                explanation = ranking_explainer.generate_explanation(
                    resource,
                    index,
                )

                resource["ranking_factors"] = (
                    explanation["factor_breakdown"]
                )

                resource["ranking_explanation"] = (
                    explanation["ranking_explanation"]
                )

        log_info(
            f"Resource ranking completed | "
            f"ranked_count={len(ranked_resources)} | "
            f"explained_top_n={min(len(ranked_resources), TOP_N_EXPLANATIONS)}"
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
