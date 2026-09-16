from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_agent_discover_e2e(monkeypatch):
    def mock_workflow_invoke(state):
        return {
            "validated_output": {
                "topic": "Greetings",
                "recommendedResources": [
                    {
                        "title": "French A1 Greetings",
                        "url": "https://example.com/french-greetings",
                    }
                ],
                "learningSequence": [
                    {
                        "order": 1,
                        "title": "Basic French Greetings",
                    }
                ],
            }
        }

    monkeypatch.setattr(
        "app.main.agent_workflow.invoke",
        mock_workflow_invoke,
    )

    response = client.post(
        "/api/agent/discover",
        json={"user_query": "French A1 Greetings"},
    )

    assert response.status_code == 200

    data = response.json()

    assert "topic" in data
    assert "recommendedResources" in data
    assert "learningSequence" in data

    assert isinstance(data["recommendedResources"], list)
    assert isinstance(data["learningSequence"], list)
