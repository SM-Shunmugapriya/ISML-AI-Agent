from services.retrieval_strategy import (
    check_existing_knowledge,
    retrieve_existing_knowledge,
)


def test_check_existing_knowledge_returns_hit_when_thresholds_are_met(monkeypatch):
    similar_resources = [
        {"id": 1, "title": "Python Basics", "url": "url1", "type": "video", "source": "youtube", "similarity_score": 0.90},
        {"id": 2, "title": "Python Functions", "url": "url2", "type": "pdf", "source": "website", "similarity_score": 0.85},
        {"id": 3, "title": "Python Loops", "url": "url3", "type": "article", "source": "website", "similarity_score": 0.80},
    ]

    class FakeResource:
        def __init__(self, resource_id, title, score):
            self.id = resource_id
            self.title = title
            self.url = f"url{resource_id}"
            self.resource_type = "article"
            self.source = "website"
            self.description = ""
            self.content = ""
            self.category = "Core Learning"
            self.tags = []
            self.relevance_score = score
            self.educational_quality = score
            self.credibility = score
            self.learning_effectiveness = score
            self.overall_score = score

    resources = [
        FakeResource(1, "Python Basics", 0.90),
        FakeResource(2, "Python Functions", 0.85),
        FakeResource(3, "Python Loops", 0.80),
    ]

    class FakeQuery:
        def filter(self, *args, **kwargs):
            return self

        def all(self):
            return resources

    class FakeDB:
        def query(self, *args, **kwargs):
            return FakeQuery()

        def close(self):
            pass

    monkeypatch.setattr(
        "services.retrieval_strategy.find_similar_resources",
        lambda query, limit=10: similar_resources,
    )
    monkeypatch.setattr(
        "services.retrieval_strategy.SessionLocal",
        lambda: FakeDB(),
    )

    is_sufficient, result = check_existing_knowledge("Python programming")

    assert is_sufficient is True
    assert len(result) == 3
    assert result[0]["overall_score"] == 0.90


def test_check_existing_knowledge_requires_three_high_quality_matches(monkeypatch):
    similar_resources = [
        {"id": 1, "title": "Python Basics", "url": "url1", "type": "video", "source": "youtube", "similarity_score": 0.90},
        {"id": 2, "title": "Python Functions", "url": "url2", "type": "pdf", "source": "website", "similarity_score": 0.85},
    ]

    class FakeQuery:
        def filter(self, *args, **kwargs):
            return self

        def all(self):
            return []

    class FakeDB:
        def query(self, *args, **kwargs):
            return FakeQuery()

        def close(self):
            pass

    monkeypatch.setattr(
        "services.retrieval_strategy.find_similar_resources",
        lambda query, limit=10: similar_resources,
    )
    monkeypatch.setattr(
        "services.retrieval_strategy.SessionLocal",
        lambda: FakeDB(),
    )

    is_sufficient, result = check_existing_knowledge("Python programming")

    assert is_sufficient is False


def test_quality_score_normalizes_percentage_values(monkeypatch):
    similar_resources = [
        {"id": 1, "title": "Python Basics", "url": "url1", "type": "video", "source": "youtube", "similarity_score": 0.90},
        {"id": 2, "title": "Python Functions", "url": "url2", "type": "pdf", "source": "website", "similarity_score": 0.85},
        {"id": 3, "title": "Python Loops", "url": "url3", "type": "article", "source": "website", "similarity_score": 0.80},
    ]

    class FakeResource:
        def __init__(self, resource_id):
            self.id = resource_id
            self.title = f"Resource {resource_id}"
            self.url = f"url{resource_id}"
            self.resource_type = "article"
            self.source = "website"
            self.description = ""
            self.content = ""
            self.category = "Core Learning"
            self.tags = []
            self.relevance_score = 90
            self.educational_quality = 90
            self.credibility = 90
            self.learning_effectiveness = 90
            self.overall_score = 90

    resources = [FakeResource(1), FakeResource(2), FakeResource(3)]

    class FakeQuery:
        def filter(self, *args, **kwargs):
            return self

        def all(self):
            return resources

    class FakeDB:
        def query(self, *args, **kwargs):
            return FakeQuery()

        def close(self):
            pass

    monkeypatch.setattr(
        "services.retrieval_strategy.find_similar_resources",
        lambda query, limit=10: similar_resources,
    )
    monkeypatch.setattr(
        "services.retrieval_strategy.SessionLocal",
        lambda: FakeDB(),
    )

    is_sufficient, result = check_existing_knowledge("Python programming")

    assert is_sufficient is True
    assert result[0]["overall_score"] == 0.90


def test_retrieval_node_routes_to_existing_knowledge(monkeypatch):
    monkeypatch.setattr(
        "services.retrieval_strategy.check_existing_knowledge",
        lambda query, limit=10: (
            True,
            [{"id": 1, "title": "Python Basics", "overall_score": 0.90}],
        ),
    )

    state = {"user_query": "Python programming"}

    result = retrieve_existing_knowledge(state)

    assert result["retrieval_hit"] is True
    assert result["retrieval_coverage"] == 1
    assert len(result["retrieved_resources"]) == 1


def test_retrieval_node_falls_back_to_discovery(monkeypatch):
    monkeypatch.setattr(
        "services.retrieval_strategy.check_existing_knowledge",
        lambda query, limit=10: (False, []),
    )

    state = {"user_query": "Quantum computing"}

    result = retrieve_existing_knowledge(state)

    assert result["retrieval_hit"] is False
    assert result["retrieved_resources"] == []


def test_repeated_topic_reuses_existing_knowledge_at_least_80_percent(monkeypatch):
    results = [
        (True, [{"id": 1}]),
        (True, [{"id": 1}]),
        (True, [{"id": 1}]),
        (True, [{"id": 1}]),
        (False, []),
    ]

    calls = {"count": 0}

    def fake_check(query, limit=10):
        result = results[calls["count"]]
        calls["count"] += 1
        return result

    monkeypatch.setattr(
        "services.retrieval_strategy.check_existing_knowledge",
        fake_check,
    )

    hits = 0

    for _ in range(5):
        result = retrieve_existing_knowledge(
            {"user_query": "Python programming"}
        )
        if result["retrieval_hit"]:
            hits += 1

    assert hits / 5 >= 0.80
