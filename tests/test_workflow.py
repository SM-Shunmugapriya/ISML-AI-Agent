import pytest

from agents.workflow import graph
from agents.resource_discovery import discover_resources


def test_complete_workflow_structure():
    expected_nodes = [
        "topic_analysis",
        "search_strategy",
        "resource_discovery",
        "metadata_extraction",
        "validation",
        "deduplication",
        "evaluation",
        "ranking",
        "categorization",
        "learning_sequence",
        "database_persistence",
        "embedding",
        "output_validation",
    ]

    for node in expected_nodes:
        assert node in graph.nodes


def test_workflow_has_all_required_nodes():
    assert len(graph.nodes) == 13


def test_resource_discovery_uses_selected_tools(monkeypatch):
    calls = []

    def mock_web_search(query, **kwargs):
        calls.append("web")
        return {
            "results": [
                {
                    "title": "Web Resource",
                    "url": "https://example.com",
                    "content": "Web content",
                    "score": 0.9,
                }
            ]
        }

    def mock_youtube_search(query, **kwargs):
        calls.append("youtube")
        return {
            "results": [
                {
                    "title": "YouTube Resource",
                    "url": "https://youtube.com/watch?v=test",
                    "channel": "Test Channel",
                    "duration": "10:00",
                    "views": 1000,
                }
            ]
        }

    def mock_pdf_search(query, **kwargs):
        calls.append("pdf")
        return {
            "results": [
                {
                    "title": "PDF Resource",
                    "url": "https://example.com/test.pdf",
                    "content": "PDF content",
                    "score": 0.8,
                }
            ]
        }

    monkeypatch.setattr(
        "agents.resource_discovery.web_search",
        mock_web_search,
    )

    monkeypatch.setattr(
        "agents.resource_discovery.youtube_search",
        mock_youtube_search,
    )

    monkeypatch.setattr(
        "agents.resource_discovery.pdf_search",
        mock_pdf_search,
    )

    state = {
        "search_queries": ["Python programming"],
        "search_tools": ["web", "youtube"],
    }

    result = discover_resources(state)

    assert calls == ["web", "youtube"]

    resources = result["resources"]

    assert len(resources) == 2
    assert resources[0]["resource_type"] == "web"
    assert resources[1]["resource_type"] == "youtube"

    assert all("title" in resource for resource in resources)
    assert all("url" in resource for resource in resources)

    assert not any(
        resource["resource_type"] == "pdf"
        for resource in resources
    )


def test_search_strategy_selects_search_tools(monkeypatch):
    def mock_ask_llm(prompt, **kwargs):
        return {
            "search_queries": [
                "Python programming basics",
                "Python beginner tutorial",
            ],
            "search_tools": [
                "web",
                "youtube",
            ],
        }

    monkeypatch.setattr(
        "agents.search_strategy.ask_llm",
        mock_ask_llm,
    )

    from agents.search_strategy import generate_search_strategy

    state = {
        "topic": "Python",
        "subtopics": ["variables", "functions"],
    }

    result = generate_search_strategy(state)

    assert "search_queries" in result
    assert "search_tools" in result
    assert len(result["search_queries"]) == 2
    assert result["search_tools"] == ["web", "youtube"]


def test_resource_discovery_multi_source_aggregation(monkeypatch):
    calls = []

    def mock_web_search(query, **kwargs):
        calls.append("web")
        return {
            "results": [
                {
                    "title": "Python Web Tutorial",
                    "url": "https://example.com/python",
                    "content": "Python web tutorial",
                    "score": 0.95,
                }
            ]
        }

    def mock_youtube_search(query, **kwargs):
        calls.append("youtube")
        return {
            "results": [
                {
                    "title": "Python YouTube Tutorial",
                    "url": "https://youtube.com/watch?v=python",
                    "channel": "Python Channel",
                    "duration": "15:00",
                    "views": 5000,
                }
            ]
        }

    def mock_pdf_search(query, **kwargs):
        calls.append("pdf")
        return {
            "results": [
                {
                    "title": "Python PDF Tutorial",
                    "url": "https://example.com/python.pdf",
                    "content": "Python PDF tutorial",
                    "score": 0.90,
                }
            ]
        }

    def mock_audio_search(query, **kwargs):
        calls.append("audio")
        return {
            "results": [
                {
                    "title": "Python Audio Tutorial",
                    "url": "https://archive.org/details/python-audio",
                    "description": "Python audio tutorial",
                }
            ]
        }

    monkeypatch.setattr(
        "agents.resource_discovery.web_search",
        mock_web_search,
    )

    monkeypatch.setattr(
        "agents.resource_discovery.youtube_search",
        mock_youtube_search,
    )

    monkeypatch.setattr(
        "agents.resource_discovery.pdf_search",
        mock_pdf_search,
    )

    monkeypatch.setattr(
        "agents.resource_discovery.audio_search",
        mock_audio_search,
    )

    state = {
        "search_queries": ["Python programming basics"],
        "search_tools": ["web", "youtube", "pdf", "audio"],
    }

    result = discover_resources(state)

    assert calls == ["web", "youtube", "pdf", "audio"]

    assert "search_results" in result
    assert "resources" in result

    resources = result["resources"]

    assert len(resources) == 4

    resource_types = {
        resource["resource_type"]
        for resource in resources
    }

    assert resource_types == {
        "web",
        "youtube",
        "pdf",
        "audio",
    }

    for resource in resources:
        assert "title" in resource
        assert "url" in resource
        assert "resource_type" in resource
        assert resource["title"]
        assert resource["url"]
        assert resource["resource_type"] in {
            "web",
            "youtube",
            "pdf",
            "audio",
        }