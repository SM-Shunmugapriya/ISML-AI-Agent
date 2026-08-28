from services.dedup_service import (
    normalize_url,
    deduplicate_resources,
)


def test_normalize_trailing_slash():
    url = "https://example.com/python/"

    result = normalize_url(url)

    assert result == "https://example.com/python"


def test_normalize_tracking_parameters():
    url = (
        "https://example.com/python"
        "?utm_source=google&utm_medium=social"
    )

    result = normalize_url(url)

    assert result == "https://example.com/python"


def test_normalize_uppercase_domain():
    url = "https://EXAMPLE.COM/python"

    result = normalize_url(url)

    assert result == "https://example.com/python"


def test_duplicate_urls_are_removed():
    resources = [
        {
            "title": "Python",
            "url": "https://example.com/python",
        },
        {
            "title": "Python Duplicate",
            "url": "https://example.com/python",
        },
    ]

    result = deduplicate_resources(resources)

    assert len(result) == 1
    assert result[0]["title"] == "Python"


def test_url_variations_are_detected_as_duplicates():
    resources = [
        {
            "title": "Python",
            "url": "https://example.com/python",
        },
        {
            "title": "Python Slash",
            "url": "https://example.com/python/",
        },
        {
            "title": "Python Tracking",
            "url": (
                "https://example.com/python"
                "?utm_source=google"
            ),
        },
    ]

    result = deduplicate_resources(resources)

    assert len(result) == 1
    assert result[0]["url"] == "https://example.com/python"


def test_different_resources_are_kept():
    resources = [
        {
            "title": "Python",
            "url": "https://example.com/python",
        },
        {
            "title": "Java",
            "url": "https://example.com/java",
        },
    ]

    result = deduplicate_resources(resources)

    assert len(result) == 2