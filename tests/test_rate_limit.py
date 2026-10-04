from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_rate_limiter_configured():
    assert app.state.limiter is not None


def test_rate_limit_routes_registered():
    rate_limited = [
        route
        for route in app.routes
        if getattr(route, "endpoint", None)
        and hasattr(route.endpoint, "__wrapped__")
    ]

    assert len(rate_limited) >= 1
