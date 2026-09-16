import pytest

from agents.workflow import app
from app.database.database import SessionLocal
from app.database.models import Resource


TEST_URLS = [
    f"https://example.com/e2e-french-a1-greetings-{i}"
    for i in range(1, 11)
]


def test_master_e2e_french_a1_greetings(monkeypatch):
    """BUG-018: Verify the complete workflow through semantic retrieval."""

    # ---------------------------------------------------------
    # Mock LLM: Topic Analysis
    # ---------------------------------------------------------
    def mock_topic_llm(prompt, provider="gemini"):
        return {
            "domain": "Language Learning",
            "course": "French",
            "topic": "Greetings",
            "level": "beginner",
            "subtopics": [
                "Basic Greetings",
                "Introductions",
            ],
            "learning_intent": "Learn basic French greetings",
        }

    # ---------------------------------------------------------
    # Mock LLM: Search Strategy
    # ---------------------------------------------------------
    def mock_search_llm(prompt, provider="gemini"):
        return {
            "search_queries": [
                "French A1 greetings",
                "French beginner greetings",
                "French basic introductions",
                "French greetings vocabulary",
                "French A1 speaking practice",
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

    # ---------------------------------------------------------
    # Mock Resource Discovery
    # ---------------------------------------------------------
    def mock_web_search(query, max_results=5):
        query_index = [
            "French A1 greetings",
            "French beginner greetings",
            "French basic introductions",
            "French greetings vocabulary",
            "French A1 speaking practice",
        ].index(query)

        start_index = query_index * 2

        return {
            "results": [
                {
                    "title": f"French A1 Greetings Resource {i + 1}",
                    "url": TEST_URLS[i],
                    "content": (
                        "French beginner greetings including "
                        "bonjour, salut and introductions."
                    ),
                    "score": 0.95,
                }
                for i in range(start_index, start_index + 2)
            ]
        }

    monkeypatch.setattr(
        "agents.resource_discovery.web_search",
        mock_web_search,
    )

    # ---------------------------------------------------------
    # Mock Metadata Extraction
    # ---------------------------------------------------------
    def mock_extract_metadata(resource, resource_type):
        return {
            "title": resource["title"],
            "url": resource["url"],
            "type": resource_type,
            "source": "E2E Test Source",
            "language": "French",
            "difficulty": "beginner",
            "summary": "French A1 greetings learning resource.",
            "keywords": [
                "French",
                "A1",
                "greetings",
            ],
        }

    monkeypatch.setattr(
        "agents.metadata_extraction.extract_metadata",
        mock_extract_metadata,
    )

    # ---------------------------------------------------------
    # Mock URL Accessibility
    # ---------------------------------------------------------
    monkeypatch.setattr(
        "agents.validation.is_url_accessible",
        lambda url: True,
    )

    # ---------------------------------------------------------
    # Mock Relevance Calculation
    # ---------------------------------------------------------
    monkeypatch.setattr(
        "agents.validation.evaluator.calculate_relevance",
        lambda topic, resource: 0.95,
    )

    # ---------------------------------------------------------
    # Mock Resource Evaluation
    # ---------------------------------------------------------
    def mock_evaluate(resource, topic):
        return {
            **resource,
            "relevance_score": 0.95,
            "quality_score": 0.95,
            "overall_score": 95.0,
        }

    monkeypatch.setattr(
        "agents.evaluation.evaluator.evaluate",
        mock_evaluate,
    )

    # ---------------------------------------------------------
    # Mock Categorization
    # ---------------------------------------------------------
    monkeypatch.setattr(
        "agents.categorization.categorize_resource",
        lambda resource: "Core Learning",
    )

    # ---------------------------------------------------------
    # Mock Embedding
    # ---------------------------------------------------------
    test_embedding = [1.0] + [0.0] * 3071

    monkeypatch.setattr(
        "agents.embedding.generate_embedding",
        lambda text: test_embedding,
    )

    # Semantic search uses its own imported embedding function.
    monkeypatch.setattr(
        "services.vector_search.generate_embedding",
        lambda text: test_embedding,
    )

    db = SessionLocal()

    try:
        # -----------------------------------------------------
        # Cleanup previous E2E data
        # -----------------------------------------------------
        existing = (
            db.query(Resource)
            .filter(Resource.url.in_(TEST_URLS))
            .all()
        )

        for resource in existing:
            db.delete(resource)

        db.commit()

        # -----------------------------------------------------
        # Execute complete workflow
        # -----------------------------------------------------
        result = app.invoke(
            {
                "user_query": "French A1 Greetings",
                "level": "beginner",
            }
        )

        # -----------------------------------------------------
        # 1. Input
        # -----------------------------------------------------
        assert result["user_query"] == "French A1 Greetings"

        # -----------------------------------------------------
        # 2. Topic Analysis
        # -----------------------------------------------------
        assert result["domain"] == "Language Learning"
        assert result["course"] == "French"
        assert result["topic"] == "Greetings"
        assert result["level"] == "beginner"
        assert isinstance(result["subtopics"], list)
        assert result["learning_intent"]

        # -----------------------------------------------------
        # 3. Search Strategy
        # -----------------------------------------------------
        assert len(result["search_queries"]) == 5
        assert result["search_tools"] == ["web"]

        # -----------------------------------------------------
        # 4. Resource Discovery
        # -----------------------------------------------------
        assert len(result["search_results"]) == 10
        assert len(result["resources"]) == 10

        # -----------------------------------------------------
        # 5. Metadata Extraction
        # -----------------------------------------------------
        assert len(result["metadata"]) == 10

        # -----------------------------------------------------
        # 6. Validation
        # -----------------------------------------------------
        assert len(result["validated_resources"]) == 10

        # -----------------------------------------------------
        # 7. Deduplication
        # -----------------------------------------------------
        assert len(result["unique_resources"]) == 10

        # -----------------------------------------------------
        # 8. Evaluation
        # -----------------------------------------------------
        assert len(result["evaluated_resources"]) == 10

        # -----------------------------------------------------
        # 9. Ranking
        # -----------------------------------------------------
        assert len(result["ranked_resources"]) == 10

        # -----------------------------------------------------
        # 10. Categorization
        # -----------------------------------------------------
        assert len(result["categorized_resources"]) == 10

        # -----------------------------------------------------
        # 11. Learning Sequence
        # -----------------------------------------------------
        assert len(result["learning_sequence"]) == 10

        # -----------------------------------------------------
        # 12. Database Persistence
        # -----------------------------------------------------
        assert len(result["persisted_resources"]) == 10

        # -----------------------------------------------------
        # 13. Embeddings
        # -----------------------------------------------------
        assert len(result["embeddings"]) == 10

        for embedding in result["embeddings"]:
            assert len(embedding) == 3072

        # -----------------------------------------------------
        # 14. Resource Success Rate
        # -----------------------------------------------------
        discovered_count = len(result["resources"])
        successful_count = len(result["validated_resources"])

        assert discovered_count == 10
        assert successful_count == 10

        success_rate = successful_count / discovered_count

        assert success_rate > 0.90

        # -----------------------------------------------------
        # 15. Verify PostgreSQL Persistence
        # -----------------------------------------------------
        saved_resources = (
            db.query(Resource)
            .filter(Resource.url.in_(TEST_URLS))
            .all()
        )

        assert len(saved_resources) == 10

        # -----------------------------------------------------
        # 16. Verify pgvector Embeddings
        # -----------------------------------------------------
        embedded_resources = [
            resource
            for resource in saved_resources
            if resource.embedding is not None
        ]

        assert len(embedded_resources) == 10

        for resource in embedded_resources:
            assert len(resource.embedding) == 3072

        # -----------------------------------------------------
        # 17. Semantic Retrieval
        # -----------------------------------------------------
        from services.vector_search import find_similar_resources

        semantic_results = find_similar_resources(
            "French A1 Greetings",
            limit=5,
        )

        assert isinstance(semantic_results, list)
        assert len(semantic_results) > 0

        for item in semantic_results:
            assert "id" in item
            assert "title" in item
            assert "url" in item
            assert "resource_type" in item
            assert "source" in item
            assert "similarity_score" in item
            assert 0 <= item["similarity_score"] <= 1

        # -----------------------------------------------------
        # 18. Final Output Schema
        # -----------------------------------------------------
        assert "validated_output" in result

        output = result["validated_output"]

        assert output["topic"] == "Greetings"
        assert "recommendedResources" in output
        assert "learningSequence" in output

        assert isinstance(
            output["recommendedResources"],
            list,
        )

        assert isinstance(
            output["learningSequence"],
            list,
        )

        assert len(output["recommendedResources"]) > 0
        assert len(output["learningSequence"]) > 0

    finally:
        # -----------------------------------------------------
        # Cleanup E2E database resources
        # -----------------------------------------------------
        cleanup = (
            db.query(Resource)
            .filter(Resource.url.in_(TEST_URLS))
            .all()
        )

        for resource in cleanup:
            db.delete(resource)

        db.commit()
        db.close()

