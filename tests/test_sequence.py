from services.sequence_service import generate_learning_sequence


def test_learning_sequence_orders_by_category():
    resources = [
        {
            "title": "Assessment Test",
            "category": "Assessment",
            "difficulty": "beginner",
            "rank": 1,
        },
        {
            "title": "English Basics",
            "category": "Foundation",
            "difficulty": "beginner",
            "rank": 2,
        },
        {
            "title": "Grammar Basics",
            "category": "Grammar",
            "difficulty": "beginner",
            "rank": 3,
        },
    ]

    result = generate_learning_sequence(resources)

    assert result[0]["title"] == "English Basics"
    assert result[1]["title"] == "Grammar Basics"
    assert result[2]["title"] == "Assessment Test"


def test_learning_order_is_assigned():
    resources = [
        {
            "title": "English Basics",
            "category": "Foundation",
            "difficulty": "beginner",
            "rank": 1,
        },
        {
            "title": "Grammar",
            "category": "Grammar",
            "difficulty": "beginner",
            "rank": 2,
        },
    ]

    result = generate_learning_sequence(resources)

    assert result[0]["learning_order"] == 1
    assert result[1]["learning_order"] == 2


def test_beginner_resources_come_before_advanced():
    resources = [
        {
            "title": "Advanced Grammar",
            "category": "Grammar",
            "difficulty": "advanced",
            "rank": 1,
        },
        {
            "title": "Basic Grammar",
            "category": "Grammar",
            "difficulty": "beginner",
            "rank": 2,
        },
    ]

    result = generate_learning_sequence(resources)

    assert result[0]["title"] == "Basic Grammar"
    assert result[1]["title"] == "Advanced Grammar"


def test_empty_resources():
    result = generate_learning_sequence([])

    assert result == []


def test_resources_are_preserved():
    resources = [
        {
            "title": "English Basics",
            "category": "Foundation",
            "difficulty": "beginner",
            "rank": 1,
            "overall_score": 0.95,
        }
    ]

    result = generate_learning_sequence(resources)

    assert result[0]["title"] == "English Basics"
    assert result[0]["category"] == "Foundation"
    assert result[0]["overall_score"] == 0.95
    assert result[0]["learning_order"] == 1


def test_learning_sequence_max_10_steps():
    resources = [
        {
            "title": f"English Resource {i}",
            "category": "Practice",
            "difficulty": "beginner",
            "rank": i,
        }
        for i in range(1, 13)
    ]

    result = generate_learning_sequence(resources)

    assert len(result) <= 10


def test_learning_order_is_continuous():
    resources = [
        {
            "title": f"Resource {i}",
            "category": "Practice",
            "difficulty": "beginner",
            "rank": i,
        }
        for i in range(1, 6)
    ]

    result = generate_learning_sequence(resources)

    orders = [resource["learning_order"] for resource in result]

    assert orders == [1, 2, 3, 4, 5]


def test_foundation_before_grammar_before_assessment():
    resources = [
        {
            "title": "Assessment Test",
            "category": "Assessment",
            "difficulty": "beginner",
            "rank": 1,
        },
        {
            "title": "Grammar Basics",
            "category": "Grammar",
            "difficulty": "beginner",
            "rank": 2,
        },
        {
            "title": "English Foundation",
            "category": "Foundation",
            "difficulty": "beginner",
            "rank": 3,
        },
    ]

    result = generate_learning_sequence(resources)

    assert result[0]["category"] == "Foundation"
    assert result[1]["category"] == "Grammar"
    assert result[2]["category"] == "Assessment"