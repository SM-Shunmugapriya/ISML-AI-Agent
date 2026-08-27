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
        "content": (
            "Learn Python programming with examples, "
            "tutorials, and practical exercises."
        ),
    }


def test_valid_resource_passes_validation(monkeypatch):
    monkeypatch.setattr(
        "agents.validation.is_url_accessible",
        lambda url: True,
    )

    state = {
        "topic": "Python programming",
        "metadata": [complete_metadata()],
    }

    result = validate_resources(state)

    assert len(result["validated_resources"]) == 1


def test_inaccessible_url_is_rejected(monkeypatch):
    monkeypatch.setattr(
        "agents.validation.is_url_accessible",
        lambda url: False,
    )

    state = {
        "topic": "Python programming",
        "metadata": [complete_metadata()],
    }

    result = validate_resources(state)

    assert result["validated_resources"] == []


def test_irrelevant_resource_is_rejected(monkeypatch):
    monkeypatch.setattr(
        "agents.validation.is_url_accessible",
        lambda url: True,
    )

    metadata = complete_metadata()
    metadata["title"] = "Cooking Recipes"
    metadata["content"] = (
        "Learn delicious cooking recipes and food preparation."
    )

    state = {
        "topic": "Python programming",
        "metadata": [metadata],
    }

    result = validate_resources(state)

    assert result["validated_resources"] == []


def test_relevant_resource_is_accepted(monkeypatch):
    monkeypatch.setattr(
        "agents.validation.is_url_accessible",
        lambda url: True,
    )

    state = {
        "topic": "Python programming",
        "metadata": [complete_metadata()],
    }

    result = validate_resources(state)

    assert len(result["validated_resources"]) == 1


def test_only_valid_resources_reach_downstream(monkeypatch):
    monkeypatch.setattr(
        "agents.validation.is_url_accessible",
        lambda url: True,
    )

    valid_resource = complete_metadata()

    invalid_resource = complete_metadata()
    invalid_resource["title"] = "Cooking Recipes"
    invalid_resource["content"] = (
        "Learn delicious cooking recipes and food preparation."
    )

    state = {
        "topic": "Python programming",
        "metadata": [
            valid_resource,
            invalid_resource,
        ],
    }

    result = validate_resources(state)

    assert len(result["validated_resources"]) == 1
    assert result["validated_resources"][0]["title"] == (
        "Python Programming Tutorial"
    )