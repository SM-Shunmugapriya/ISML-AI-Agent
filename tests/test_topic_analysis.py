import pytest
from agents.topic_analysis import analyze_topic


def test_analyze_topic_success(monkeypatch):
    expected = {
        "domain": "Language Learning",
        "course": "French",
        "topic": "Greetings",
        "level": "beginner",
        "subtopics": ["Hello", "Goodbye"],
        "learning_intent": "Learn basic French greetings"
    }

    def mock_ask_llm(prompt):
        assert "French A1 Greetings" in prompt
        return expected

    monkeypatch.setattr(
        "agents.topic_analysis.ask_llm",
        mock_ask_llm
    )

    result = analyze_topic({
        "user_query": "French A1 Greetings"
    })

    for key, value in expected.items():
        assert result[key] == value


def test_analyze_topic_with_workflow_run_id(monkeypatch):
    def mock_ask_llm(prompt, workflow_run_id=None):
        assert workflow_run_id == "test-run-123"
        return {"topic": "Greetings"}

    monkeypatch.setattr(
        "agents.topic_analysis.ask_llm",
        mock_ask_llm
    )

    result = analyze_topic({
        "user_query": "French greetings",
        "workflow_run_id": "test-run-123"
    })

    assert result["topic"] == "Greetings"


def test_analyze_topic_missing_fields_uses_defaults(monkeypatch):
    monkeypatch.setattr(
        "agents.topic_analysis.ask_llm",
        lambda prompt: {}
    )

    result = analyze_topic({
        "user_query": "Learn French",
        "domain": "Language",
        "course": "French",
        "topic": "Basics",
        "level": "beginner"
    })

    assert result["domain"] == "Language"
    assert result["course"] == "French"
    assert result["topic"] == "Basics"
    assert result["level"] == "beginner"
    assert result["subtopics"] == []
    assert result["learning_intent"] == ""


def test_analyze_topic_llm_error(monkeypatch):
    def mock_ask_llm(prompt):
        raise RuntimeError("LLM service unavailable")

    monkeypatch.setattr(
        "agents.topic_analysis.ask_llm",
        mock_ask_llm
    )

    with pytest.raises(RuntimeError, match="LLM service unavailable"):
        analyze_topic({
            "user_query": "Learn French"
        })
