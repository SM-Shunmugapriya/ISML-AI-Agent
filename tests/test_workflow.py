from agents.workflow import graph
from agents.resource_discovery import discover_resources


def test_complete_workflow_structure():
    nodes = graph.nodes

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
    ]

    for node in expected_nodes:
        assert node in nodes


def test_workflow_has_all_required_nodes():
    assert len(graph.nodes) == 12


def test_resource_discovery_uses_selected_tools(monkeypatch):
    calls = []

    def mock_web_search(query, max_results=5):
        calls.append("web")
        return {
            "query": query,
            "results": [
                {
                    "title": "Python Tutorial",
                    "url": "https://example.com/python",
                    "content": "Python tutorial",
                    "score": 0.95,
                }
            ],
        }

    def mock_youtube_search(query, max_results=5):
        calls.append("youtube")
        return {
            "query": query,
            "results": [
                {
                    "title": "Python Video",
                    "url": "https://youtube.com/watch?v=123",
                    "channel": "Python Channel",
                    "duration": "10:00",
                    "views": "1000",
                }
            ],
        }

    def mock_pdf_search(query, max_results=5):
        calls.append("pdf")
        return {
            "query": query,
            "results": [
                {
                    "title": "Python PDF",
                    "url": "https://example.com/python.pdf",
                    "content": "Python notes",
                    "score": 0.90,
                }
            ],
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
        "user_query": "Python programming basics",
        "topic": "Python Programming",
        "subtopics": ["Variables", "Functions"],
        "learning_intent": "Learn Python basics",
        "search_queries": [
            "Python programming basics"
        ],
        "search_tools": [
            "web",
            "youtube",
        ],
    }

    result = discover_resources(state)

    assert calls == ["web", "youtube"]

    assert "search_results" in result
    assert "resources" in result
    assert len(result["resources"]) == 2

    resource_types = {
        resource["resource_type"]
        for resource in result["resources"]
    }

    assert "web" in resource_types
    assert "youtube" in resource_types
    assert "pdf" not in resource_types


def test_search_strategy_selects_search_tools(monkeypatch):
    def mock_ask_llm(prompt, provider="gemini"):
        return {
            "search_queries": [
                "Python programming basics",
                "Python functions tutorial",
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
        "user_query": "Learn Python",
        "topic": "Python Programming",
        "subtopics": [
            "Variables",
            "Functions",
        ],
        "learning_intent": "Learn Python basics",
    }

    result = generate_search_strategy(state)

    assert result["search_queries"] == [
        "Python programming basics",
        "Python functions tutorial",
    ]

    assert result["search_tools"] == [
        "web",
        "youtube",
    ]