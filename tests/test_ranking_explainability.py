from agents.ranking import rank_resources


def test_ranking_generates_explanations_for_top_5():
    resources = []

    for index in range(6):
        resources.append({
            "title": f"Resource {index + 1}",
            "overall_score": 95.0 - index,
            "scores": {
                "relevance": 0.95 - (index * 0.01),
                "educational_quality": 0.90,
                "credibility": 0.85,
                "learning_effectiveness": 0.80,
            },
        })

    state = {
        "evaluated_resources": resources,
    }

    result = rank_resources(state)
    ranked = result["ranked_resources"]

    assert len(ranked) == 6

    assert ranked[0]["rank"] == 1
    assert ranked[0]["overall_score"] == 95.0

    assert "ranking_factors" in ranked[0]
    assert "ranking_explanation" in ranked[0]

    assert ranked[0]["ranking_factors"]["relevance"] == 95.0
    assert ranked[0]["ranking_factors"]["educational_quality"] == 90.0
    assert ranked[0]["ranking_factors"]["credibility"] == 85.0
    assert ranked[0]["ranking_factors"]["learning_effectiveness"] == 80.0

    assert "Ranked #1" in ranked[0]["ranking_explanation"]

    assert "ranking_factors" not in ranked[5]
    assert "ranking_explanation" not in ranked[5]


def test_ranking_empty_resources():
    state = {
        "evaluated_resources": [],
    }

    result = rank_resources(state)

    assert result["ranked_resources"] == []