from agents.categorization import categorize_resources
from services.categorization_service import deterministic_category


def test_deterministic_categories():
    test_cases = [
        (
            {
                "title": "English Grammar Test",
                "summary": "Quiz on tenses and nouns",
                "keywords": ["assessment", "test"],
            },
            "Assessment",
        ),
        (
            {
                "title": "English Listening Practice",
                "summary": "Audio conversations for learners",
                "keywords": ["listening"],
            },
            "Listening",
        ),
        (
            {
                "title": "English Vocabulary Words",
                "summary": "Common words and synonyms",
                "keywords": ["vocabulary"],
            },
            "Vocabulary",
        ),
        (
            {
                "title": "English Pronunciation Guide",
                "summary": "Learn correct pronunciation",
                "keywords": ["pronunciation"],
            },
            "Pronunciation",
        ),
        (
            {
                "title": "English Revision Workbook",
                "summary": "Review previous lessons",
                "keywords": ["revision"],
            },
            "Revision",
        ),
        (
            {
                "title": "English Speaking Practice",
                "summary": "Oral conversation activities",
                "keywords": ["speaking"],
            },
            "Speaking",
        ),
        (
            {
                "title": "English Basics for Beginners",
                "summary": "Fundamentals of English",
                "keywords": ["beginner", "basics"],
            },
            "Foundation",
        ),
        (
            {
                "title": "English Exercise Workbook",
                "summary": "Exercises for learners",
                "keywords": ["exercise", "workbook"],
            },
            "Practice",
        ),
    ]

    for resource, expected_category in test_cases:
        result = deterministic_category(resource)
        assert result == expected_category


def test_categorization_node(monkeypatch):
    """
    Test the categorization LangGraph node.

    The LLM call is mocked so this test does not depend
    on Gemini/API availability.
    """

    def mock_categorize_resource(resource):
        return deterministic_category(resource)

    monkeypatch.setattr(
        "agents.categorization.categorize_resource",
        mock_categorize_resource,
    )

    state = {
        "ranked_resources": [
            {
                "title": "English Grammar Test",
                "summary": "Quiz on basic grammar",
                "keywords": ["assessment", "test"],
                "type": "quiz",
                "difficulty": "beginner",
                "overall_score": 0.9,
                "rank": 1,
            }
        ]
    }

    result = categorize_resources(state)

    assert "categorized_resources" in result
    assert len(result["categorized_resources"]) == 1

    categorized_resource = result["categorized_resources"][0]

    assert categorized_resource["category"] == "Assessment"
    assert categorized_resource["title"] == "English Grammar Test"
    assert categorized_resource["rank"] == 1


def test_multiple_resources_categorization(monkeypatch):
    """
    Test that multiple resources receive
    appropriate pedagogical categories.
    """

    def mock_categorize_resource(resource):
        return deterministic_category(resource)

    monkeypatch.setattr(
        "agents.categorization.categorize_resource",
        mock_categorize_resource,
    )

    state = {
        "ranked_resources": [
            {
                "title": "English Grammar Test",
                "summary": "Test on grammar",
                "keywords": ["grammar", "test"],
            },
            {
                "title": "English Listening Practice",
                "summary": "Audio listening exercises",
                "keywords": ["listening", "audio"],
            },
            {
                "title": "English Vocabulary Guide",
                "summary": "Common English words",
                "keywords": ["vocabulary", "words"],
            },
        ]
    }

    result = categorize_resources(state)

    categorized_resources = result["categorized_resources"]

    assert len(categorized_resources) == 3

    assert categorized_resources[0]["category"] == "Assessment"
    assert categorized_resources[1]["category"] == "Listening"
    assert categorized_resources[2]["category"] == "Vocabulary"


def test_empty_resources():
    """
    Test categorization when no resources are available.
    """

    state = {
        "ranked_resources": []
    }

    result = categorize_resources(state)

    assert "categorized_resources" in result
    assert result["categorized_resources"] == []


def test_category_is_valid(monkeypatch):
    """
    Ensure every categorized resource receives
    one of the allowed pedagogical categories.
    """

    allowed_categories = {
        "Core Learning",
        "Foundation",
        "Practice",
        "Revision",
        "Pronunciation",
        "Grammar",
        "Vocabulary",
        "Listening",
        "Speaking",
        "Assessment",
        "Supplementary",
    }

    def mock_categorize_resource(resource):
        return deterministic_category(resource)

    monkeypatch.setattr(
        "agents.categorization.categorize_resource",
        mock_categorize_resource,
    )

    state = {
        "ranked_resources": [
            {
                "title": "English Grammar",
                "summary": "Learn English grammar rules",
                "keywords": ["grammar"],
            },
            {
                "title": "English Speaking Practice",
                "summary": "Practice spoken English",
                "keywords": ["speaking"],
            },
            {
                "title": "English Revision",
                "summary": "Review previous lessons",
                "keywords": ["revision"],
            },
        ]
    }

    result = categorize_resources(state)

    for resource in result["categorized_resources"]:
        assert resource["category"] in allowed_categories