import os

from dotenv import load_dotenv
from google import genai

from services.resilience_service import (
    retry_with_backoff,
    CircuitBreaker,
)


load_dotenv()


client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options={"timeout": 30000},
)


EMBEDDING_CIRCUIT_BREAKER = CircuitBreaker(
    failure_threshold=5
)

EMBEDDING_MODEL = "gemini-embedding-001"
DEFAULT_BATCH_SIZE = 50
EMBEDDING_DIMENSIONS = 3072


def _embed_batch_request(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for multiple texts in one API request."""

    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=texts,
        config={"output_dimensionality": EMBEDDING_DIMENSIONS},
    )

    embeddings = response.embeddings or []

    if len(embeddings) != len(texts):
        raise ValueError(
            f"Embedding count mismatch: expected {len(texts)}, "
            f"received {len(embeddings)}"
        )

    results = []

    for embedding in embeddings:
        values = embedding.values

        if values is None or len(values) != EMBEDDING_DIMENSIONS:
            raise ValueError(
                "Gemini returned an embedding with an invalid dimension"
            )

        results.append(list(values))

    return results


def generate_embeddings_batch(
    texts: list[str],
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> list[list[float]]:
    """
    Generate embeddings in batches while preserving input order.

    Empty or whitespace-only texts are rejected to avoid silently
    returning embeddings that cannot be mapped to their inputs.
    """

    if batch_size < 1:
        raise ValueError("batch_size must be at least 1")

    if not texts:
        return []

    if any(not isinstance(text, str) or not text.strip() for text in texts):
        raise ValueError("Texts must contain non-empty strings")

    all_embeddings = []

    for start in range(0, len(texts), batch_size):
        batch = texts[start:start + batch_size]

        resilient_request = retry_with_backoff(
            max_retries=3,
            backoff_factor=1,
            timeout=30,
            circuit_breaker=EMBEDDING_CIRCUIT_BREAKER,
        )(
            lambda current_batch=batch: _embed_batch_request(current_batch)
        )

        all_embeddings.extend(resilient_request())

    return all_embeddings


def generate_embedding(text: str) -> list[float]:
    """Generate one vector embedding, preserving the existing API."""

    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    return generate_embeddings_batch([text])[0]
