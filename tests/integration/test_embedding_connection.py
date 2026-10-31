import math
import os

import pytest

from services.embedding_service import generate_embedding


@pytest.mark.integration
@pytest.mark.skipif(
    os.getenv("RUN_LIVE_INTEGRATION") != "1",
    reason="Live integration tests are disabled",
)
def test_embedding_live_connection():
    if not os.getenv("GEMINI_API_KEY"):
        pytest.skip("GEMINI_API_KEY is not configured")

    embedding = generate_embedding(
        "Integration test for embedding service"
    )

    assert isinstance(embedding, list)
    assert len(embedding) == 3072

    assert all(
        isinstance(value, (int, float)) and math.isfinite(value)
        for value in embedding
    )
