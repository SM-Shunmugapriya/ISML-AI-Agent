from typing import Any, Dict

from pydantic import ValidationError

from agents.state import AgentState
from services.output_schema import FinalOutput
from services.output_repair import repair_output
from services.logger import log_info, log_error


MAX_REPAIR_ATTEMPTS = 2


def validate_final_output(state: AgentState) -> AgentState:
    """
    Validate final agent output and attempt repair when validation fails.
    """

    topic = state.get("topic", "")
    resources = state.get("categorized_resources", [])
    learning_sequence = state.get("learning_sequence", [])

    log_info(
        f"Final output validation started | "
        f"resources_count={len(resources)} | "
        f"sequence_count={len(learning_sequence)}"
    )

    recommended_resources = []

    for resource in resources:
        recommended_resources.append({
            "title": resource.get("title", ""),
            "type": resource.get(
                "type",
                resource.get("resource_type", "")
            ),
            "qualityScore": resource.get(
                "overall_score",
                0.0
            ),
            "difficulty": resource.get("difficulty", ""),
            "category": resource.get("category", ""),
            "summary": resource.get(
                "summary",
                resource.get("description", "")
            ),
            "url": resource.get("url", ""),
        })

    formatted_learning_sequence = []

    for resource in learning_sequence:
        formatted_learning_sequence.append({
            "title": resource.get("title", ""),
            "type": resource.get(
                "type",
                resource.get("resource_type", "")
            ),
            "qualityScore": resource.get(
                "overall_score",
                0.0
            ),
            "difficulty": resource.get("difficulty", ""),
            "category": resource.get("category", ""),
            "summary": resource.get(
                "summary",
                resource.get("description", "")
            ),
            "url": resource.get("url", ""),
        })

    output_data: Dict[str, Any] = {
        "topic": topic,
        "recommendedResources": recommended_resources,
        "learningSequence": formatted_learning_sequence,
    }

    for attempt in range(1, MAX_REPAIR_ATTEMPTS + 1):
        try:
            validated_output = FinalOutput.model_validate(output_data)

            log_info(
                f"Final output validation successful | attempt={attempt}"
            )

            return {
                **state,
                "validated_output": validated_output.model_dump(),
            }

        except ValidationError as e:
            log_error(
                f"Final output validation failed | "
                f"attempt={attempt} | error={e}"
            )

            if attempt >= MAX_REPAIR_ATTEMPTS:
                raise ValueError(
                    f"Invalid final output after "
                    f"{MAX_REPAIR_ATTEMPTS} repair attempts: {e}"
                ) from e

            log_info(
                f"Attempting final output repair | "
                f"attempt={attempt}"
            )

            output_data = repair_output(output_data)

           
            

    raise ValueError("Final output validation failed")