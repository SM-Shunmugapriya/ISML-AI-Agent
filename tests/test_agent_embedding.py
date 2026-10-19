from unittest.mock import MagicMock

from agents import embedding as agent_embedding


def make_resource(resource_id, title="Python"):
    resource = MagicMock()
    resource.id = resource_id
    resource.title = title
    resource.embedding = None
    resource.processing_status = "pending"
    return resource


def make_db(resource_map):
    db = MagicMock()
    query = db.query.return_value
    query.filter.return_value.first.side_effect = (
        lambda: resource_map.get(db.query.call_args[0][0])
    )
    return db


def test_resources_are_embedded_in_one_batch_and_saved(monkeypatch):
    first = make_resource(1, "Python")
    second = make_resource(2, "AI")
    db = MagicMock()
    query = db.query.return_value
    query.filter.return_value.first.side_effect = [first, second]
    monkeypatch.setattr(agent_embedding, "SessionLocal", lambda: db)

    captured = {}

    def fake_batch(texts, batch_size):
        captured["texts"] = texts
        captured["batch_size"] = batch_size
        return [[0.1] * 3072, [0.2] * 3072]

    monkeypatch.setattr(
        agent_embedding, "generate_embeddings_batch", fake_batch
    )

    state = {
        "persisted_resources": [
            {
                "database_id": 1,
                "resource": {
                    "title": "Python",
                    "description": "Basics",
                    "content": "Variables",
                },
            },
            {
                "database_id": 2,
                "resource": {
                    "title": "AI",
                    "description": "Intro",
                    "content": "Models",
                },
            },
        ]
    }

    result = agent_embedding.generate_resource_embeddings(state)

    assert len(captured["texts"]) == 2
    assert captured["batch_size"] == 50
    assert first.processing_status == "completed"
    assert second.processing_status == "completed"
    assert len(first.embedding) == 3072
    assert len(second.embedding) == 3072
    assert len(result["embeddings"]) == 2
    db.commit.assert_called_once()
    db.close.assert_called_once()


def test_empty_resources_skip_batch_call(monkeypatch):
    db = MagicMock()
    monkeypatch.setattr(agent_embedding, "SessionLocal", lambda: db)

    def unexpected_batch(*args, **kwargs):
        raise AssertionError("Batch API should not be called")

    monkeypatch.setattr(
        agent_embedding, "generate_embeddings_batch", unexpected_batch
    )

    result = agent_embedding.generate_resource_embeddings(
        {"persisted_resources": []}
    )

    assert result["embeddings"] == []
    db.commit.assert_called_once()
    db.close.assert_called_once()


def test_batch_failure_rolls_back_database(monkeypatch):
    db = MagicMock()
    monkeypatch.setattr(agent_embedding, "SessionLocal", lambda: db)

    def fail_batch(*args, **kwargs):
        raise RuntimeError("simulated embedding failure")

    monkeypatch.setattr(
        agent_embedding, "generate_embeddings_batch", fail_batch
    )

    state = {
        "persisted_resources": [
            {
                "database_id": 1,
                "resource": {
                    "title": "Python",
                    "description": "",
                    "content": "Basics",
                },
            }
        ]
    }

    result = agent_embedding.generate_resource_embeddings(state)

    assert result["embeddings"] == []
    db.rollback.assert_called_once()
    db.commit.assert_not_called()
    db.close.assert_called_once()
