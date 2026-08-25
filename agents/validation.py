from typing import List, Dict, Any

from agents.state import AgentState
from services.logger import log_info, log_error


# Required fields that must be preserved
# throughout the entire workflow.
REQUIRED_STATE_FIELDS = [
    "domain",
    "course",
    "topic",
    "level",
]


def validate_state(state: AgentState) -> AgentState:
    """
    Validate that all required topic-understanding
    fields are present in the workflow state.
    """

    log_info("Workflow state validation started")

    try:
        missing_fields = []

        for field in REQUIRED_STATE_FIELDS:
            value = state.get(field)

            if value is None or (
                isinstance(value, str) and not value.strip()
            ):
                missing_fields.append(field)

        if missing_fields:
            error_message = (
                "Required workflow state fields are missing: "
                + ", ".join(missing_fields)
            )

            log_error(error_message)

            raise ValueError(error_message)

        log_info(
            "Workflow state validation passed | "
            f"domain={state.get('domain')} | "
            f"course={state.get('course')} | "
            f"topic={state.get('topic')} | "
            f"level={state.get('level')}"
        )

        return state

    except Exception as e:
        log_error(
            f"Workflow state validation failed | error={e}"
        )
        raise


def validate_resources(state: AgentState) -> AgentState:
    metadata = state.get("metadata", [])

    log_info(
        f"Resource validation started | resources_count={len(metadata)}"
    )

    validated_resources: List[Dict[str, Any]] = []

    try:
        for resource in metadata:
            title = resource.get("title", "").strip()
            url = resource.get("url", "").strip()

            if not title or not url:
                continue

            if not url.startswith(("http://", "https://")):
                continue

            validated_resources.append(resource)

        log_info(
            f"Resource validation completed | "
            f"valid_count={len(validated_resources)}"
        )

        return {
            **state,
            "validated_resources": validated_resources,
        }

    except Exception as e:
        log_error(
            f"Resource validation failed | error={e}"
        )
        raise