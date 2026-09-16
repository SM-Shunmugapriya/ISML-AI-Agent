import pytest
from agents.metadata_extraction import extract_resource_metadata


def test_failed_resource_is_skipped_and_processing_continues(monkeypatch):
    resources = [
        {
            "title": "Failed Resource",
            "url": "https://example.com/fail",
            "resource_type": "web",
        },
        {
            "title": "Successful Resource",
            "url": "https://example.com/success",
            "resource_type": "web",
        },
    ]

    def mock_extract_metadata(resource, resource_type):
        if resource["title"] == "Failed Resource":
            raise ValueError("Extraction failed")

        return {
            "title": "Successful Resource",
            "url": "https://example.com/success",
            "type": "Course",
            "source": "Web",
            "language": "English",
            "difficulty": "Beginner",
            "summary": "Python basics",
            "keywords": ["python"],
        }

    monkeypatch.setattr(
        "agents.metadata_extraction.extract_metadata",
        mock_extract_metadata,
    )

    state = {"resources": resources}

    result = extract_resource_metadata(state)

    assert len(result["metadata"]) == 1
    assert result["metadata"][0]["title"] == "Successful Resource"


def test_all_resources_are_processed_even_when_one_fails(monkeypatch):
    calls = []

    resources = [
        {
            "title": "Resource 1",
            "url": "https://example.com/1",
            "resource_type": "web",
        },
        {
            "title": "Resource 2",
            "url": "https://example.com/2",
            "resource_type": "web",
        },
        {
            "title": "Resource 3",
            "url": "https://example.com/3",
            "resource_type": "web",
        },
    ]

    def mock_extract_metadata(resource, resource_type):
        calls.append(resource["title"])

        if resource["title"] == "Resource 2":
            raise ValueError("Bad resource")

        return {
            "title": resource["title"],
            "url": resource["url"],
            "type": "Course",
            "source": "Web",
            "language": "English",
            "difficulty": "Beginner",
            "summary": "Test resource",
            "keywords": ["test"],
        }

    monkeypatch.setattr(
        "agents.metadata_extraction.extract_metadata",
        mock_extract_metadata,
    )

    result = extract_resource_metadata({"resources": resources})

    assert calls == ["Resource 1", "Resource 2", "Resource 3"]
    assert len(result["metadata"]) == 2
