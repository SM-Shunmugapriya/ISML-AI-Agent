from typing import List, Dict, Any

from agents.state import AgentState
from services.logger import log_info, log_error


def create_learning_sequence(state: AgentState) -> AgentState:
    resources = state.get("categorized_resources", [])

    log_info(
        f"Learning sequence creation started | resources_count={len(resources)}"
    )

    try:
        learning_sequence: List[Dict[str, Any]] = []

        for index, resource in enumerate(resources, start=1):
            learning_sequence.append({
                **resource,
                "learning_order": index,
            })

        log_info(
            f"Learning sequence created | sequence_count={len(learning_sequence)}"
        )

        return {
            **state,
            "learning_sequence": learning_sequence,
        }

    except Exception as e:
        log_error(
            f"Learning sequence creation failed | error={e}"
        )
        raise