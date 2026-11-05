import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


@pytest.mark.parametrize("path", ["/", "/v1/health"])
def test_public_endpoints_remain_available(path):
    response = client.get(path)

    assert response.status_code == 200


def test_health_response_contract():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "ISML AI Agent",
    }


def test_protected_resource_endpoint_rejects_invalid_api_key(monkeypatch):
    monkeypatch.setenv("ISML_API_KEY", "correct-key")

    response = client.get(
        "/resources",
        headers={"X-API-Key": "wrong-key"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthorized"


def test_discover_rejects_blank_query(monkeypatch):
    monkeypatch.setenv("ISML_API_KEY", "test-api-key")

    response = client.post(
        "/api/agent/discover",
        json={"user_query": "   "},
        headers={"X-API-Key": "test-api-key"},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


@pytest.mark.parametrize(
    "path",
    ["/api/agent/discover", "/v1/api/agent/discover"],
)
def test_agent_discover_workflow_contract(monkeypatch, path):
    monkeypatch.setenv("ISML_API_KEY", "test-api-key")

    class FakeObservability:
        def start_run(self, input_data):
            return "regression-test-run"

        def record_counts(self, **kwargs):
            pass

        def finish_run(self, status):
            return {"duration_seconds": 0.1}

        def record_error(self, **kwargs):
            pass

    monkeypatch.setattr(
        "app.main.ObservabilityService",
        FakeObservability,
    )

    expected_output = {
        "topic": "French Greetings",
        "recommendedResources": [
            {
                "title": "French A1 Greetings",
                "url": "https://example.com/greetings",
            }
        ],
        "learningSequence": [
            {
                "order": 1,
                "title": "Basic Greetings",
            }
        ],
    }

    monkeypatch.setattr(
        "app.main.agent_workflow.invoke",
        lambda state: {"validated_output": expected_output},
    )

    response = client.post(
        path,
        json={"user_query": "French A1 Greetings"},
        headers={"X-API-Key": "test-api-key"},
    )

    assert response.status_code == 200
    assert response.json() == expected_output
