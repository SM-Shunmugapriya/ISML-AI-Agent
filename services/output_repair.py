from typing import Any, Dict

from services.output_schema import FinalOutput
from services.llm_service import ask_llm


def repair_output(
    output_data: Dict[str, Any],
    provider: str = "gemini",
) -> Dict[str, Any]:
    """
    Repair invalid final output using the LLM and validate
    the repaired result against the final output schema.
    """

    prompt = f"""
Repair the following invalid JSON output so that it strictly
matches the required schema.

IMPORTANT RULES:
1. Preserve all existing valid values.
2. Do NOT replace existing valid values with empty strings.
3. Every required string field MUST contain a meaningful
   non-empty value.
4. qualityScore MUST be a number between 0 and 100.
5. If a required field is missing or empty, infer a suitable
   meaningful value from the resource title, topic, and
   other available information.
6. Do NOT remove any resource.
7. Do NOT create empty values for required fields.
8. The url field MUST contain a non-empty URL.
9. Return ONLY the repaired JSON object.
10. Do not add explanations or markdown.

Required structure:

{{
    "topic": "string",
    "recommendedResources": [
        {{
            "title": "string",
            "type": "string",
            "qualityScore": "number between 0 and 100",
            "difficulty": "string",
            "category": "string",
            "summary": "string",
            "url": "string"
        }}
    ],
    "learningSequence": [
        {{
            "title": "string",
            "type": "string",
            "qualityScore": "number between 0 and 100",
            "difficulty": "string",
            "category": "string",
            "summary": "string",
            "url": "string"
        }}
    ]
}}

Original invalid output:
{output_data}

Return ONLY the repaired JSON object.
"""

    repaired_output = ask_llm(prompt, provider=provider)

    if not isinstance(repaired_output, dict):
        raise ValueError("LLM repair response is not a dictionary")

    

    return FinalOutput.model_validate(repaired_output).model_dump()
