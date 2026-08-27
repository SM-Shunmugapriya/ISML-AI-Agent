from agents.validation import validate_resources


def complete_metadata():
    return {
        "title": "Python Programming Tutorial",
        "url": "https://example.com/python",
        "type": "web",
        "source": "Web",
        "language": "English",
        "difficulty": "Beginner",
        "summary": "A beginner Python programming tutorial.",
        "keywords": ["python", "programming", "tutorial"],
    }


def test_complete_metadata_is_accepted():
    state = {
        "metadata": [complete_metadata()]
    }

    result = validate_resources(state)

    assert len(result["validated_resources"]) == 1
    assert result["validated_resources"][0]["title"] == (
        "Python Programming Tutorial"
    )


def test_missing_required_metadata_is_rejected():
    metadata = complete_metadata()
    metadata["language"] = ""

    state = {
        "metadata": [metadata]
    }

    result = validate_resources(state)

    assert result["validated_resources"] == []


def test_missing_keywords_is_rejected():
    metadata = complete_metadata()
    metadata["keywords"] = []

    state = {
        "metadata": [metadata]
    }

    result = validate_resources(state)

    assert result["validated_resources"] == []


def test_invalid_url_is_rejected():
    metadata = complete_metadata()
    metadata["url"] = "example.com/python"

    state = {
        "metadata": [metadata]
    }

    result = validate_resources(state)

    assert result["validated_resources"] == []


def test_only_complete_resources_proceed():
    valid_resource = complete_metadata()

    invalid_resource = complete_metadata()
    invalid_resource["summary"] = ""

    state = {
        "metadata": [
            valid_resource,
            invalid_resource,
        ]
    }

    result = validate_resources(state)

    assert len(result["validated_resources"]) == 1
    assert result["validated_resources"][0]["title"] == (
        "Python Programming Tutorial"
    )