import pytest

from services import embedding_service


def test_empty_batch_returns_empty_list():
    assert embedding_service.generate_embeddings_batch([]) == []


def test_invalid_batch_size_raises_error():
    with pytest.raises(ValueError, match="batch_size"):
        embedding_service.generate_embeddings_batch(["hello"], batch_size=0)


def test_empty_text_is_rejected():
    with pytest.raises(ValueError, match="non-empty strings"):
        embedding_service.generate_embeddings_batch(["hello", " "])


def test_batch_processing_preserves_order_and_chunks(monkeypatch):
    calls = []

    def fake_embed_batch(texts):
        calls.append(list(texts))
        return [[float(len(texts)), float(index)] for index, _ in enumerate(texts)]

    monkeypatch.setattr(embedding_service, "_embed_batch_request", fake_embed_batch)
    monkeypatch.setattr(
        embedding_service,
        "retry_with_backoff",
        lambda **kwargs: lambda func: func,
    )

    result = embedding_service.generate_embeddings_batch(
        ["one", "two", "three", "four", "five"],
        batch_size=2,
    )

    assert calls == [["one", "two"], ["three", "four"], ["five"]]
    assert result == [[2.0, 0.0], [2.0, 1.0], [2.0, 0.0], [2.0, 1.0], [1.0, 0.0]]


def test_single_embedding_keeps_existing_interface(monkeypatch):
    monkeypatch.setattr(
        embedding_service,
        "generate_embeddings_batch",
        lambda texts: [[0.25] * embedding_service.EMBEDDING_DIMENSIONS],
    )

    result = embedding_service.generate_embedding("hello")

    assert len(result) == embedding_service.EMBEDDING_DIMENSIONS
    assert result[0] == 0.25
