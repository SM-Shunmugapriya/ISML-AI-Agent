def extract_metadata(resource: dict, resource_type: str):
    metadata = {
        "title": resource.get("title", ""),
        "url": resource.get("url", ""),
        "resource_type": resource_type,
        "source": "",
        "description": resource.get("content", ""),
    }

    url = resource.get("url", "")

    if "youtube.com" in url or "youtu.be" in url:
        metadata["source"] = "YouTube"
    elif url.lower().endswith(".pdf"):
        metadata["source"] = "PDF"
    else:
        metadata["source"] = "Web"

    return metadata
