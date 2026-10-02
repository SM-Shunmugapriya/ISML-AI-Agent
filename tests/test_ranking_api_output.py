from agents.output_validation import validate_final_output


def test_ranking_explanation_visible_in_api_output():
    state = {
        "topic": "Python",
        "categorized_resources": [
            {
                "title": "Python Course",
                "type": "Course",
                "overall_score": 94.0,
                "difficulty": "Beginner",
                "category": "Core Learning",
                "summary": "Python programming course",
                "url": "https://example.com/python",
                "ranking_factors": {
                    "relevance": 95.0,
                    "educational_quality": 92.0,
                    "credibility": 94.0,
                    "learning_effectiveness": 95.0,
                },
                "ranking_explanation": (
                    "Ranked #1 with a quality score of 94.0."
                ),
            }
        ],
        "learning_sequence": [],
    }

    result = validate_final_output(state)
    resource = result["validated_output"]["recommendedResources"][0]

    assert resource["qualityScore"] == 94.0
    assert resource["rankingFactors"]["relevance"] == 95.0
    assert resource["rankingFactors"]["educational_quality"] == 92.0
    assert resource["rankingFactors"]["credibility"] == 94.0
    assert resource["rankingFactors"]["learning_effectiveness"] == 95.0
    assert "Ranked #1" in resource["rankingExplanation"]
