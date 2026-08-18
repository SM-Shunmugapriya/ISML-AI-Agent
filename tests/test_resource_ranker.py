from services.resource_ranker import ResourceRanker


def test_rank_resources_returns_all_resources():
    ranker = ResourceRanker()

    resources = [
        {
            "title": "Python Basics",
            "url": "https://www.python.org/tutorial/",
            "content": "Learn Python programming with examples."
        },
        {
            "title": "Random Cooking Guide",
            "url": "https://example.com/cooking",
            "content": "Cooking recipes and food preparation."
        },
        {
            "title": "Python Advanced Tutorial",
            "url": "https://github.com/example/python",
            "content": "Python programming advanced examples and practice."
        }
    ]

    result = ranker.rank_resources(
        resources,
        "Python programming"
    )

    assert len(result) == 3


def test_rank_resources_sorted_high_to_low():
    ranker = ResourceRanker()

    resources = [
        {
            "title": "Cooking Guide",
            "url": "https://example.com/cooking",
            "content": "Food and cooking recipes."
        },
        {
            "title": "Python Programming Tutorial",
            "url": "https://www.python.org/tutorial/",
            "content": "Learn Python programming with examples."
        }
    ]

    result = ranker.rank_resources(
        resources,
        "Python programming"
    )

    scores = [item["overall_score"] for item in result]

    assert scores == sorted(scores, reverse=True)


def test_rank_resources_contains_scores():
    ranker = ResourceRanker()

    resources = [
        {
            "title": "Python Tutorial",
            "url": "https://www.python.org/tutorial/",
            "content": "Python tutorial with examples."
        }
    ]

    result = ranker.rank_resources(
        resources,
        "Python"
    )

    assert len(result) == 1
    assert "scores" in result[0]
    assert "overall_score" in result[0]


def test_get_recommendations_default_top_three():
    ranker = ResourceRanker()

    resources = [
        {
            "title": f"Python Tutorial {i}",
            "url": "https://www.python.org/tutorial/",
            "content": "Learn Python programming with examples."
        }
        for i in range(5)
    ]

    result = ranker.get_recommendations(
        resources,
        "Python programming"
    )

    assert len(result) == 3


def test_get_recommendations_custom_top_n():
    ranker = ResourceRanker()

    resources = [
        {
            "title": f"Python Tutorial {i}",
            "url": "https://www.python.org/tutorial/",
            "content": "Learn Python programming with examples."
        }
        for i in range(5)
    ]

    result = ranker.get_recommendations(
        resources,
        "Python programming",
        top_n=2
    )

    assert len(result) == 2


def test_empty_resource_list():
    ranker = ResourceRanker()

    result = ranker.rank_resources(
        [],
        "Python programming"
    )

    assert result == []