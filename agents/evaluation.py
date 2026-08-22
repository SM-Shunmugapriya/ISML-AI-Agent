from typing import List, Dict, Any

from agents.state import AgentState
from services.resource_evaluator import ResourceEvaluator
from services.logger import log_info, log_error


evaluator = ResourceEvaluator()


def evaluate_resources(state: AgentState) -> AgentState:
    resources = state.get("unique_resources", [])
    topic = state.get("topic", "")

    log_info(
        f"Resource evaluation started | resources_count={len(resources)}"
    )

    evaluated_resources: List[Dict[str, Any]] = []

    try:
        for resource in resources:
            evaluation = evaluator.evaluate(
                resource,
                topic
            )

            evaluated_resources.append(evaluation)

        log_info(
            f"Resource evaluation completed | evaluated_count={len(evaluated_resources)}"
        )

        return {
            **state,
            "evaluated_resources": evaluated_resources,
        }

    except Exception as e:
        log_error(
            f"Resource evaluation failed | error={e}"
        )
        raise