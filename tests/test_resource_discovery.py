from tools.metadata_extractor import extract_metadata
from tools.pdf_search import pdf_search
from tools.web_search import web_search
from tools.youtube_search import youtube_search


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
    result = web_search("Python programming", max_results=2)

    assert isinstance(result, dict)
    assert "results" in result
    assert len(result["results"]) <= 2


def test_youtube_search():
    result = youtube_search("Python programming tutorial", max_results=2)

    assert isinstance(result, dict)
    assert result["query"] == "Python programming tutorial"
    assert "results" in result
    assert len(result["results"]) <= 2


def test_pdf_search():
    result = pdf_search("machine learning", max_results=2)

    assert isinstance(result, dict)
    assert result["query"] == "machine learning"
    assert "results" in result
    assert len(result["results"]) <= 2