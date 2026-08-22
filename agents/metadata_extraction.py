from typing import List, Dict, Any

from agents.state import AgentState
from tools.metadata_extractor import extract_metadata
from services.logger import log_info, log_error


def extract_resource_metadata(state: AgentState) -> AgentState:
    resources = state.get("resources", [])

    log_info(
        f"Metadata extraction started | resources_count={len(resources)}"
    )

    metadata: List[Dict[str, Any]] = []

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

            metadata.append({
                **resource,
                **extracted
            })

        log_info(
            f"Metadata extraction completed | metadata_count={len(metadata)}"
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