import pytest

from agents.state import AgentState
from agents.validation import validate_state


def create_valid_state() -> AgentState:
    return {
        "user_query": "I want to learn Python programming",
        "domain": "Computer Science",
        "course": "Python Programming",
        "topic": "Python",
        "level": "beginner",
    }


def test_state_contains_all_required_fields():
    state = create_valid_state()

    result = validate_state(state)

    assert result["domain"] == "Computer Science"
    assert result["course"] == "Python Programming"
    assert result["topic"] == "Python"
    assert result["level"] == "beginner"


def test_state_validation_passes_with_all_required_fields():
    state = create_valid_state()

    result = validate_state(state)

    assert result == state


def test_state_validation_fails_when_domain_is_missing():
    state = create_valid_state()
    del state["domain"]

    with pytest.raises(ValueError, match="domain"):
        validate_state(state)


def test_state_validation_fails_when_course_is_missing():
    state = create_valid_state()
    del state["course"]

    with pytest.raises(ValueError, match="course"):
        validate_state(state)


def test_state_validation_fails_when_topic_is_missing():
    state = create_valid_state()
    del state["topic"]

    with pytest.raises(ValueError, match="topic"):
        validate_state(state)


def test_state_validation_fails_when_level_is_missing():
    state = create_valid_state()
    del state["level"]

    with pytest.raises(ValueError, match="level"):
        validate_state(state)


def test_state_validation_fails_when_multiple_fields_are_missing():
    state = create_valid_state()

    del state["domain"]
    del state["course"]
    del state["level"]

    with pytest.raises(ValueError) as error:
        validate_state(state)

    error_message = str(error.value)

    assert "domain" in error_message
    assert "course" in error_message
    assert "level" in error_message