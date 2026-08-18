from services.vector_search import find_similar_resources


def test_semantic_search_returns_results():
    results = find_similar_resources("machine learning", limit=5)

    assert isinstance(results, list)
    assert len(results) > 0


def test_semantic_search_result_structure():
    results = find_similar_resources("python programming", limit=5)

    assert len(results) > 0

    result = results[0]

    assert "id" in result
    assert "title" in result
    assert "url" in result
    assert "resource_type" in result
    assert "source" in result
    assert "similarity_score" in result


def test_semantic_search_similarity_score():
    results = find_similar_resources("machine learning", limit=5)

    assert len(results) > 0

    for result in results:
        assert 0 <= result["similarity_score"] <= 1


def test_semantic_search_empty_query():
    try:
        find_similar_resources("")
        assert False
    except ValueError:
        assert True