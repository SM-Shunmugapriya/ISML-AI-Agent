from typing import List, Dict, Any

from agents.state import AgentState
from services.logger import log_info, log_error
from services.sequence_service import generate_learning_sequence


def create_learning_sequence(state: AgentState) -> AgentState:
    resources = state.get("categorized_resources", [])

    log_info(
        f"Learning sequence creation started | resources_count={len(resources)}"
    )

    try:
        learning_sequence: List[Dict[str, Any]] = generate_learning_sequence(
            resources
        )

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
