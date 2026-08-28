from typing import Any, Dict, List
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


TRACKING_PARAMS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "gclid",
    "fbclid",
    "msclkid",
}


def normalize_url(url: str) -> str:
    """
    Normalize a URL so common variations of the same resource
    are treated as the same URL.
    """

    if not url:
        return ""

    url = url.strip()

    try:
        parts = urlsplit(url)

        scheme = parts.scheme.lower()
        netloc = parts.netloc.lower()

        # Remove trailing slash from path
        path = parts.path.rstrip("/")

        # Remove common tracking parameters
        query_params = parse_qsl(
            parts.query,
            keep_blank_values=True
        )

        filtered_params = [
            (key, value)
            for key, value in query_params
            if key.lower() not in TRACKING_PARAMS
        ]

        query = urlencode(filtered_params)

        return urlunsplit(
            (
                scheme,
                netloc,
                path,
                query,
                ""
            )
        )

    except ValueError:
        return url


def deduplicate_resources(
    resources: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Remove duplicate resources using normalized URLs.
    """

    unique_resources: List[Dict[str, Any]] = []
    seen_urls = set()

    for resource in resources:
        url = resource.get("url", "")

        normalized_url = normalize_url(url)

        if not normalized_url:
            continue

        if normalized_url in seen_urls:
            continue

        seen_urls.add(normalized_url)

        unique_resource = {
            **resource,
            "url": normalized_url,
        }

        unique_resources.append(unique_resource)

    return unique_resources