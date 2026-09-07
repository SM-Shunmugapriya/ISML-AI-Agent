from agents.database_persistence import persist_resources
from app.database.database import SessionLocal
from app.database.models import Resource


def test_persist_resources():
    test_url = "https://example.com/bug-012-test"

    db = SessionLocal()

    try:
        # Remove test resource if it already exists
        existing = (
            db.query(Resource)
            .filter(Resource.url == test_url)
            .first()
        )

        if existing:
            db.delete(existing)
            db.commit()

        state = {
            "learning_sequence": [
                {
                    "title": "Python Testing Guide",
                    "url": test_url,
                    "resource_type": "web",
                    "source": "Example",
                    "category": "Practice",
                    "keywords": ["python", "testing", "pytest"],
                    "description": "Test resource for database persistence.",
                    "content": "Python testing content.",
                    "scores": {
                        "relevance": 0.9,
                        "educational_quality": 0.85,
                        "credibility": 0.8,
                        "learning_effectiveness": 0.9,
                    },
                    "overall_score": 0.86,
                    "learning_order": 1,
                }
            ]
        }

        result = persist_resources(state)

        assert len(result["persisted_resources"]) == 1

        saved = (
            db.query(Resource)
            .filter(Resource.url == test_url)
            .first()
        )

        assert saved is not None
        assert saved.title == "Python Testing Guide"
        assert saved.category == "Practice"
        assert saved.tags == ["python", "testing", "pytest"]
        assert saved.relevance_score == 0.9
        assert saved.overall_score == 0.86

    finally:
        existing = (
            db.query(Resource)
            .filter(Resource.url == test_url)
            .first()
        )

        if existing:
            db.delete(existing)
            db.commit()

        db.close()