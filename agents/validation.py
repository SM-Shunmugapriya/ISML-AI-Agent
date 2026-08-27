from typing import List, Dict, Any
import requests

from agents.state import AgentState
from services.logger import log_info, log_error, log_warning
from services.resource_evaluator import ResourceEvaluator


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


# Minimum relevance score required for a resource
RELEVANCE_THRESHOLD = 0.3


# Reuse the existing resource evaluation logic
evaluator = ResourceEvaluator()


def is_url_accessible(url: str) -> bool:
    """
    Check whether a resource URL is accessible.

    Returns True when the URL responds with a successful
    HTTP status code. HEAD is tried first, followed by GET
    when HEAD is not supported or fails.
    """

    try:
        response = requests.head(
            url,
            timeout=5,
            allow_redirects=True,
        )

        if response.status_code < 400:
            return True

        response = requests.get(
            url,
            timeout=5,
            allow_redirects=True,
            stream=True,
        )

        return response.status_code < 400

    except requests.RequestException as e:
        log_warning(
            f"URL accessibility check failed | "
            f"url={url} | error={e}"
        )
        return False


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

    Validation includes:
    - Required metadata fields
    - Keywords structure
    - URL format
    - URL accessibility
    - Resource relevance

    Invalid or irrelevant resources are rejected and do not
    proceed to downstream processing.
    """

    metadata = state.get("metadata", [])
    topic = state.get("topic", "")

    log_info(
        f"Resource validation started | "
        f"resources_count={len(metadata)} | "
        f"topic={topic}"
    )

    validated_resources: List[Dict[str, Any]] = []
    rejected_count = 0

    try:
        for index, resource in enumerate(metadata):
            missing_fields = []

            # Validate required metadata fields
            for field in REQUIRED_METADATA_FIELDS:
                value = resource.get(field)

                if value is None:
                    missing_fields.append(field)

                elif isinstance(value, str) and not value.strip():
                    missing_fields.append(field)

                elif field == "keywords":
                    if not isinstance(value, list) or not value:
                        missing_fields.append(field)

            # Validate URL format
            url = resource.get("url", "")

            if url and not url.startswith(("http://", "https://")):
                missing_fields.append("url")

            # Reject immediately if metadata or URL format is invalid
            if missing_fields:
                rejected_count += 1

                log_error(
                    f"Resource rejected | index={index} | "
                    f"missing_or_invalid_fields="
                    f"{', '.join(sorted(set(missing_fields)))}"
                )

                continue

            # Validate URL accessibility
            if not is_url_accessible(url):
                rejected_count += 1

                log_error(
                    f"Resource rejected | index={index} | "
                    f"reason=url_not_accessible | "
                    f"url={url}"
                )

                continue

            # Validate resource relevance
            relevance_score = evaluator.calculate_relevance(
                topic,
                resource,
            )

            if relevance_score < RELEVANCE_THRESHOLD:
                rejected_count += 1

                log_error(
                    f"Resource rejected | index={index} | "
                    f"reason=low_relevance | "
                    f"relevance_score={relevance_score} | "
                    f"threshold={RELEVANCE_THRESHOLD} | "
                    f"topic={topic}"
                )

                continue

            # Resource passed all validation checks
            validated_resources.append(resource)

            log_info(
                f"Resource validation passed | "
                f"index={index} | "
                f"url={url} | "
                f"relevance_score={relevance_score}"
            )

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