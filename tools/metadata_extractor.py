from typing import Dict, Any


def extract_metadata(
    resource: Dict[str, Any],
    resource_type: str
) -> Dict[str, Any]:
    """
    Extract and normalize structured metadata from a discovered resource.
    Missing metadata fields are kept empty so they can be rejected
    by the validation stage.
    """

    url = resource.get("url", "")

    if "youtube.com" in url or "youtu.be" in url:
        source = "YouTube"
    elif url.lower().endswith(".pdf"):
        source = "PDF"
    else:
        source = "Web"

    return {
        "title": resource.get("title", "").strip(),
        "url": url.strip(),
        "type": resource.get(
            "type",
            resource.get("resource_type", resource_type)
        ),
        "source": resource.get("source", source),
        "language": resource.get("language", ""),
        "difficulty": resource.get("difficulty", ""),
        "summary": resource.get(
            "summary",
            resource.get("description", resource.get("content", ""))
        ),
        "keywords": resource.get("keywords", []),
        "resource_type": resource_type,
        "description": resource.get("content", ""),
    }