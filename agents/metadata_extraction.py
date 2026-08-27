from typing import List, Dict, Any

from agents.state import AgentState
from tools.metadata_extractor import extract_metadata
from services.logger import log_info, log_error


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


def is_valid_metadata(metadata: Dict[str, Any]) -> bool:
    """
    Validate that all required metadata fields are present
    and contain meaningful values.
    """

    for field in REQUIRED_METADATA_FIELDS:
        value = metadata.get(field)

        if value is None:
            return False

        if isinstance(value, str) and not value.strip():
            return False

        if isinstance(value, (list, dict)) and not value:
            return False

    return True


def extract_resource_metadata(state: AgentState) -> AgentState:
    """
    Extract metadata from discovered resources and reject
    resources with incomplete required metadata.
    """

    resources = state.get("resources", [])

    log_info(
        f"Metadata extraction started | resources_count={len(resources)}"
    )

    metadata: List[Dict[str, Any]] = []
    rejected_count = 0

    try:
        for resource in resources:

            resource_type = resource.get(
                "resource_type",
                "web"
            )

            extracted = extract_metadata(
                resource,
                resource_type
            )

            complete_metadata = {
                **resource,
                **extracted
            }

            # Check all required metadata fields
            if not is_valid_metadata(complete_metadata):
                rejected_count += 1

                missing_fields = [
                    field
                    for field in REQUIRED_METADATA_FIELDS
                    if not complete_metadata.get(field)
                ]

                log_info(
                    "Metadata validation failed | "
                    f"title={complete_metadata.get('title', '')} | "
                    f"missing_fields={missing_fields} | "
                    "resource rejected"
                )

                continue

            metadata.append(complete_metadata)

        log_info(
            f"Metadata extraction completed | "
            f"metadata_count={len(metadata)} | "
            f"rejected_count={rejected_count}"
        )

        return {
            **state,
            "metadata": metadata,
        }

    except Exception as e:
        log_error(
            f"Metadata extraction failed | error={e}"
        )
        raise