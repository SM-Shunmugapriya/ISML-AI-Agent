from agents.ranking import rank_resources


def test_ranking_uses_evaluation_scores():
    state = {
        "topic": "Python Programming",
        "evaluated_resources": [
            {
                "resource": {
                    "title": "Python Course A"
                },
                "overall_score": 75.0,
            },
            {
                "resource": {
                    "title": "Python Course B"
                },
                "overall_score": 95.0,
            },
            {
                "resource": {
                    "title": "Python Course C"
                },
                "overall_score": 85.0,
            },
        ],
    }

    result = rank_resources(state)

    ranked_resources = result["ranked_resources"]

    assert len(ranked_resources) == 3

    scores = [
        resource["overall_score"]
        for resource in ranked_resources
    ]

    assert scores == [95.0, 85.0, 75.0]


def test_ranking_assigns_rank_numbers():
    state = {
        "evaluated_resources": [
            {
                "resource": {
                    "title": "Resource A"
                },
                "overall_score": 80.0,
            },
            {
                "resource": {
                    "title": "Resource B"
                },
                "overall_score": 90.0,
            },
        ],
    }

    result = rank_resources(state)

    ranked_resources = result["ranked_resources"]

    assert ranked_resources[0]["rank"] == 1
    assert ranked_resources[1]["rank"] == 2


def test_ranking_returns_ranked_resources():
    state = {
        "evaluated_resources": [
            {
                "resource": {
                    "title": "Python Tutorial"
                },
                "overall_score": 92.5,
            },
        ],
    }

    result = rank_resources(state)

    assert "ranked_resources" in result
    assert len(result["ranked_resources"]) == 1


def test_ranking_contains_explanation():
    state = {
        "evaluated_resources": [
            {
                "resource": {
                    "title": "Python Tutorial"
                },
                "overall_score": 95.0,
            },
            {
                "resource": {
                    "title": "Python Guide"
                },
                "overall_score": 80.0,
            },
        ],
    }

    result = rank_resources(state)

    ranked_resources = result["ranked_resources"]

    assert len(ranked_resources) == 2

    assert "ranking_explanation" in ranked_resources[0]
    assert "ranking_explanation" in ranked_resources[1]

    assert ranked_resources[0]["ranking_explanation"] == (
        "Ranked #1 based on a composite quality score of 95.0."
    )

    assert ranked_resources[1]["ranking_explanation"] == (
        "Ranked #2 based on a composite quality score of 80.0."
    )


def test_empty_evaluated_resources():
    state = {
        "evaluated_resources": []
    }

    result = rank_resources(state)

    assert "ranked_resources" in result
    assert result["ranked_resources"] == []


def test_ranking_preserves_evaluation_scores():
    state = {
        "evaluated_resources": [
            {
                "resource": {
                    "title": "Python Course"
                },
                "scores": {
                    "relevance": 0.9,
                    "educational_quality": 0.8,
                    "credibility": 0.95,
                    "learning_effectiveness": 0.8,
                },
                "overall_score": 86.0,
            }
        ]
    }

    result = rank_resources(state)

    ranked_resource = result["ranked_resources"][0]

    assert ranked_resource["overall_score"] == 86.0
    assert ranked_resource["scores"]["relevance"] == 0.9
    assert ranked_resource["scores"]["educational_quality"] == 0.8
    assert ranked_resource["scores"]["credibility"] == 0.95
    assert ranked_resource["scores"]["learning_effectiveness"] == 0.8


def test_evaluation_results_flow_into_ranking():
    state = {
        "topic": "Python Programming",
        "evaluated_resources": [
            {
                "resource": {
                    "title": "Low Quality Python Resource"
                },
                "scores": {
                    "relevance": 0.6,
                    "educational_quality": 0.6,
                    "credibility": 0.5,
                    "learning_effectiveness": 0.6,
                },
                "overall_score": 58.0,
            },
            {
                "resource": {
                    "title": "High Quality Python Resource"
                },
                "scores": {
                    "relevance": 0.95,
                    "educational_quality": 0.9,
                    "credibility": 1.0,
                    "learning_effectiveness": 0.9,
                },
                "overall_score": 93.25,
            },
        ],
    }

    result = rank_resources(state)

    ranked_resources = result["ranked_resources"]

    assert ranked_resources[0]["resource"]["title"] == (
        "High Quality Python Resource"
    )

    assert ranked_resources[0]["overall_score"] == 93.25
    assert ranked_resources[0]["rank"] == 1

    assert ranked_resources[1]["resource"]["title"] == (
        "Low Quality Python Resource"
    )

    assert ranked_resources[1]["overall_score"] == 58.0
    assert ranked_resources[1]["rank"] == 2

    assert "ranking_explanation" in ranked_resources[0]
    assert "ranking_explanation" in ranked_resources[1]
