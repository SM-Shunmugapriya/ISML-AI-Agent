from tools.metadata_extractor import extract_metadata
from tools.pdf_search import pdf_search
from tools.web_search import web_search
from tools.youtube_search import youtube_search
from agents.resource_discovery import discover_resources


def test_metadata_extractor():
    resource = {
        "title": "Python Tutorial",
        "url": "https://example.com/python",
        "content": "Python programming tutorial"
    }

    result = extract_metadata(resource, "web")

    assert result["title"] == "Python Tutorial"
    assert result["url"] == "https://example.com/python"
    assert result["resource_type"] == "web"
    assert result["source"] == "Web"


def test_metadata_extractor_youtube():
    resource = {
        "title": "Python Course",
        "url": "https://www.youtube.com/watch?v=123",
        "content": "Python course video"
    }

    result = extract_metadata(resource, "video")

    assert result["source"] == "YouTube"


def test_metadata_extractor_pdf():
    resource = {
        "title": "Machine Learning PDF",
        "url": "https://example.com/machine-learning.pdf",
        "content": "Machine learning notes"
    }

    result = extract_metadata(resource, "pdf")

    assert result["source"] == "PDF"


def test_web_search():
    result = web_search(
        "Python programming",
        max_results=2
    )

    assert isinstance(result, dict)
    assert "results" in result
    assert len(result["results"]) <= 2


def test_youtube_search():
    result = youtube_search(
        "Python programming tutorial",
        max_results=2
    )

    assert isinstance(result, dict)
    assert result["query"] == "Python programming tutorial"
    assert "results" in result
    assert len(result["results"]) <= 2


def test_pdf_search():
    result = pdf_search(
        "machine learning",
        max_results=2
    )

    assert isinstance(result, dict)
    assert result["query"] == "machine learning"
    assert "results" in result
    assert len(result["results"]) <= 2


def test_resource_discovery():
    state = {
        "search_queries": ["Python programming"]
    }

    result = discover_resources(state)

    assert "search_results" in result
    assert "resources" in result
    assert isinstance(result["search_results"], list)
    assert isinstance(result["resources"], list)


def test_multi_source_resource_discovery(monkeypatch):
    state = {
        "search_queries": ["Python programming"],
        "search_tools": ["web", "youtube", "pdf", "audio"]
    }

    monkeypatch.setattr(
        "agents.resource_discovery.web_search",
        lambda query, max_results=5: {
            "results": [
                {
                    "title": "Python Web Tutorial",
                    "url": "https://example.com/python",
                    "content": "Python programming tutorial",
                    "score": 0.9
                }
            ]
        }
    )

    monkeypatch.setattr(
        "agents.resource_discovery.youtube_search",
        lambda query, max_results=5: {
            "results": [
                {
                    "title": "Python YouTube Tutorial",
                    "url": "https://youtube.com/watch?v=test123",
                    "channel": "Python Channel",
                    "duration": "10:00",
                    "views": "1000 views"
                }
            ]
        }
    )

    monkeypatch.setattr(
        "agents.resource_discovery.pdf_search",
        lambda query, max_results=5: {
            "results": [
                {
                    "title": "Python PDF Notes",
                    "url": "https://example.com/python.pdf",
                    "content": "Python notes",
                    "score": 0.8
                }
            ]
        }
    )

    monkeypatch.setattr(
        "agents.resource_discovery.audio_search",
        lambda query, max_results=5: {
            "results": [
                {
                    "title": "Python Audio Lecture",
                    "url": "https://archive.org/details/python-audio",
                    "description": "Python programming audio lecture"
                }
            ]
        }
    )

    result = discover_resources(state)

    resources = result["resources"]

    assert isinstance(resources, list)

    source_types = {
        resource["resource_type"]
        for resource in resources
    }

    assert "web" in source_types
    assert "youtube" in source_types
    assert "pdf" in source_types
    assert "audio" in source_types

    assert len(resources) == 4

    for resource in resources:
        assert "title" in resource
        assert "url" in resource
        assert "resource_type" in resource