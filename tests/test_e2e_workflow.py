import pytest

from agents.workflow import app


def test_end_to_end_workflow(monkeypatch):
    """Verify the complete workflow without external API calls."""

    def mock_topic_llm(prompt, provider="gemini"):
        return {
            "domain": "Programming",
            "course": "Python",
            "topic": "Python Basics",
            "level": "beginner",
            "subtopics": ["Syntax", "Variables", "Data Types"],
            "learning_intent": "Learn Python programming basics",
        }

    def mock_search_llm(prompt, provider="gemini"):
        return {
            "search_queries": [
                "Python programming basics",
                "Python beginner syntax",
            ],
            "search_tools": ["web"],
        }

    monkeypatch.setattr(
        "agents.topic_analysis.ask_llm",
        mock_topic_llm,
    )

    monkeypatch.setattr(
        "agents.search_strategy.ask_llm",
        mock_search_llm,
    )

    monkeypatch.setattr(
        "agents.resource_discovery.web_search",
        lambda query, max_results=5: {
            "results": [
                {
                    "title": "Python Basics",
                    "url": "https://example.com/python-basics",
                    "content": "Python beginner programming basics.",
                    "score": 0.95,
                }
            ]
        },
    )

    monkeypatch.setattr(
        "agents.metadata_extraction.extract_metadata",
        lambda resource, resource_type: {
            "title": resource["title"],
            "url": resource["url"],
            "type": resource_type,
            "source": "E2E Test Source",
            "language": "English",
            "difficulty": "beginner",
            "summary": "Python programming basics.",
            "keywords": ["Python", "basics"],
        },
    )

    monkeypatch.setattr(
        "agents.validation.is_url_accessible",
        lambda url: True,
    )

    monkeypatch.setattr(
        "agents.validation.evaluator.calculate_relevance",
        lambda topic, resource: 0.95,
    )

    monkeypatch.setattr(
        "agents.evaluation.evaluator.evaluate",
        lambda resource, topic: {
            **resource,
            "relevance_score": 0.95,
            "quality_score": 0.95,
            "overall_score": 95.0,
        },
    )

    monkeypatch.setattr(
        "agents.categorization.categorize_resource",
        lambda resource: "Core Learning",
    )

    test_embedding = [1.0] + [0.0] * 3071

    monkeypatch.setattr(
        "agents.embedding.generate_embedding",
        lambda text: test_embedding,
    )

    monkeypatch.setattr(
        "services.vector_search.generate_embedding",
        lambda text: test_embedding,
    )

    result = app.invoke(
        {
            "user_query": "Learn Python programming basics",
        }
    )

    assert result["topic"] == "Python Basics"
    assert result["level"] == "beginner"

    assert result["search_queries"]
    assert result["search_tools"] == ["web"]

    assert result["resources"]
    assert result["metadata"]
    assert result["validated_resources"]
    assert result["unique_resources"]
    assert result["evaluated_resources"]
    assert result["ranked_resources"]
    assert result["categorized_resources"]
    assert result["learning_sequence"]
    assert result["persisted_resources"]

    assert result["embeddings"]
    assert all(len(embedding) == 3072 for embedding in result["embeddings"])

    assert "validated_output" in result

    output = result["validated_output"]

    assert "topic" in output
    assert "recommendedResources" in output
    assert "learningSequence" in output

    assert isinstance(output["recommendedResources"], list)
    assert isinstance(output["learningSequence"], list)
