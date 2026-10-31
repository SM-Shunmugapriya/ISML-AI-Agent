import os

import pytest

from tools.web_search import web_search


@pytest.mark.integration
@pytest.mark.skipif(
    os.getenv("RUN_LIVE_INTEGRATION") != "1",
    reason="Live integration tests are disabled",
)
def test_tavily_live_connection():
    if not os.getenv("TAVILY_API_KEY"):
        pytest.skip("TAVILY_API_KEY is not configured")

    response = web_search(
        query="Python programming documentation",
        max_results=1,
        retries=1,
    )

    assert isinstance(response, dict)
    assert response.get("results"), (
        "Tavily returned no results; check API connectivity"
    )
