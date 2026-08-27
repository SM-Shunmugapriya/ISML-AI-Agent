from typing import List, Dict, Any

from agents.state import AgentState
from services.logger import log_info, log_error


# Required fields for workflow state validation
REQUIRED_STATE_FIELDS = [
    "domain",
    "course",
    "topic",
    "level",
]


# Required metadata fields for every resource
REQUIRED_METADATA_FIELDS = [
    "title",
    "url",
    "type",
    "source",
    "language",
    "difficulty",
    "summary",
    "keywords",
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
    """
    Validate that every extracted resource contains
    complete and valid required metadata.

    Incomplete resources are rejected and do not proceed
    to downstream processing.
    """

    metadata = state.get("metadata", [])

    log_info(
        f"Resource validation started | "
        f"resources_count={len(metadata)}"
    )

    validated_resources: List[Dict[str, Any]] = []
    rejected_count = 0

    try:
        for index, resource in enumerate(metadata):
            missing_fields = []

            for field in REQUIRED_METADATA_FIELDS:
                value = resource.get(field)

                if value is None:
                    missing_fields.append(field)

                elif isinstance(value, str) and not value.strip():
                    missing_fields.append(field)

                elif field == "keywords":
                    if not isinstance(value, list) or not value:
                        missing_fields.append(field)

            url = resource.get("url", "")

            if url and not url.startswith(("http://", "https://")):
                missing_fields.append("url")

            if missing_fields:
                rejected_count += 1

                log_error(
                    f"Resource rejected | index={index} | "
                    f"missing_or_invalid_fields="
                    f"{', '.join(sorted(set(missing_fields)))}"
                )

                continue

            validated_resources.append(resource)

        log_info(
            f"Resource validation completed | "
            f"valid_count={len(validated_resources)} | "
            f"rejected_count={rejected_count}"
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