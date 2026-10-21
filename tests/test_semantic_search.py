
from types import SimpleNamespace

from services.vector_search import find_similar_resources


def mock_resource(resource_id, title, url, resource_type, source):
    return SimpleNamespace(
        id=resource_id,
        title=title,
        url=url,
        resource_type=resource_type,
        source=source,
    )


def mock_search_results(db, query_embedding, limit=5):
    resources = [
        (
            mock_resource(
                1,
                "Machine Learning Basics",
                "https://example.com/machine-learning",
                "article",
                "Test Source",
            ),
            0.10,
        ),
        (
            mock_resource(
                2,
                "Python Programming",
                "https://example.com/python",
                "tutorial",
                "Test Source",
            ),
            0.25,
        ),
    ]

    return resources[:limit]


def setup_semantic_search_mocks(monkeypatch):
    test_embedding = [1.0] + [0.0] * 3071

    monkeypatch.setattr(
        "services.vector_search.generate_embedding",
        lambda query: test_embedding,
    )

    monkeypatch.setattr(
        "services.vector_search.search_similar_resources",
        mock_search_results,
    )


def test_semantic_search_returns_results(monkeypatch):
    setup_semantic_search_mocks(monkeypatch)

    results = find_similar_resources("machine learning", limit=5)

    assert isinstance(results, list)
    assert len(results) > 0


def test_semantic_search_result_structure(monkeypatch):
    setup_semantic_search_mocks(monkeypatch)

    results = find_similar_resources("python programming", limit=5)

    assert len(results) > 0

    result = results[0]

    assert "id" in result
    assert "title" in result
    assert "url" in result
    assert "resource_type" in result
    assert "source" in result
    assert "similarity_score" in result


def test_semantic_search_similarity_score(monkeypatch):
    setup_semantic_search_mocks(monkeypatch)

    results = find_similar_resources("machine learning", limit=5)

    assert len(results) > 0

    for result in results:
        assert 0 <= result["similarity_score"] <= 1


def test_semantic_search_empty_query():
    try:
        find_similar_resources("")
        assert False, "Expected ValueError for an empty query"
    except ValueError:
        pass
