from services.resource_evaluator import ResourceEvaluator


def test_relevance_score():
    evaluator = ResourceEvaluator()

    resource = {
        "title": "Python Programming Tutorial",
        "content": "Learn Python programming with examples and exercises."
    }

    score = evaluator.calculate_relevance(
        "Python programming",
        resource
    )

    assert 0.0 <= score <= 1.0
    assert score > 0.0


def test_educational_quality():
    evaluator = ResourceEvaluator()

    resource = {
        "title": "Python Programming Tutorial",
        "content": (
            "Learn Python with examples, lessons, "
            "and practical exercises."
        )
    }

    score = evaluator.calculate_educational_quality(resource)

    assert 0.0 <= score <= 1.0
    assert score > 0.0


def test_credibility_edu():
    evaluator = ResourceEvaluator()

    resource = {
        "url": "https://example.edu/python"
    }

    score = evaluator.calculate_credibility(resource)

    assert score == 1.0


def test_credibility_python():
    evaluator = ResourceEvaluator()

    resource = {
        "url": "https://www.python.org/tutorial/"
    }

    score = evaluator.calculate_credibility(resource)

    assert score == 0.95


def test_credibility_github():
    evaluator = ResourceEvaluator()

    resource = {
        "url": "https://github.com/example/python"
    }

    score = evaluator.calculate_credibility(resource)

    assert score == 0.85


def test_learning_effectiveness():
    evaluator = ResourceEvaluator()

    resource = {
        "title": "Python Practical Tutorial",
        "content": (
            "Learn Python with examples, exercises, "
            "practice, projects, and code."
        )
    }

    score = evaluator.calculate_learning_effectiveness(resource)

    assert 0.0 <= score <= 1.0
    assert score == 1.0


def test_full_evaluation():
    evaluator = ResourceEvaluator()

    resource = {
        "title": "Python Programming Tutorial",
        "url": "https://www.python.org/tutorial/",
        "content": (
            "Learn Python programming with examples, "
            "exercises, practice and practical projects."
        )
    }

    result = evaluator.evaluate(
        resource,
        topic="Python programming"
    )

    assert "resource" in result
    assert "scores" in result
    assert "overall_score" in result

    assert 0.0 <= result["overall_score"] <= 1.0

    scores = result["scores"]

    assert 0.0 <= scores["relevance"] <= 1.0
    assert 0.0 <= scores["educational_quality"] <= 1.0
    assert 0.0 <= scores["credibility"] <= 1.0
    assert 0.0 <= scores["learning_effectiveness"] <= 1.0