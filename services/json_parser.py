import json


def parse_json_response(response: str) -> dict:
    """
    Parse an LLM response string into a Python dictionary.
    """
    try:
        return json.loads(response)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON response: {e}")