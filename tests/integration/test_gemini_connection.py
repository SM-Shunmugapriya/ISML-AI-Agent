import os

import pytest

from services.gemini_service import ask_gemini


@pytest.mark.integration
@pytest.mark.skipif(
    os.getenv("RUN_LIVE_INTEGRATION") != "1",
    reason="Live integration tests are disabled",
)
def test_gemini_live_connection():
    if not os.getenv("GEMINI_API_KEY"):
        pytest.skip("GEMINI_API_KEY is not configured")

    response = ask_gemini(
        'Return valid JSON only: {"status": "connected"}'
    )

    assert isinstance(response, dict)
    assert response.get("status") == "connected"
