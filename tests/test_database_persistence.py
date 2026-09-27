from agents.database_persistence import persist_resources
from app.database.database import SessionLocal
from app.database.models import Resource


def test_persist_resources():
    test_url = "https://example.com/gap-004-persistence-test"

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

        persisted_item = result["persisted_resources"][0]

        # Verify database ID is returned
        assert "database_id" in persisted_item
        assert persisted_item["database_id"] is not None

        saved = (
            db.query(Resource)
            .filter(Resource.url == test_url)
            .first()
        )

        assert saved is not None

        # Verify persisted metadata
        assert saved.title == "Python Testing Guide"
        assert saved.category == "Practice"
        assert saved.tags == ["python", "testing", "pytest"]

        # Verify persisted scores
        assert saved.relevance_score == 0.9
        assert saved.educational_quality == 0.85
        assert saved.credibility == 0.8
        assert saved.learning_effectiveness == 0.9
        assert saved.overall_score == 0.86

        # Verify processing status
        assert saved.processing_status == "pending"

        # Verify returned ID matches database ID
        assert persisted_item["database_id"] == saved.id

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


def test_persist_resources_handles_duplicate_url():
    test_url = "https://example.com/gap-004-duplicate-test"

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
                    "title": "Duplicate Test Resource",
                    "url": test_url,
                    "resource_type": "web",
                    "source": "Example",
                    "category": "Practice",
                    "keywords": ["python"],
                    "description": "Duplicate handling test.",
                    "content": "Test content.",
                    "scores": {
                        "relevance": 0.9,
                    },
                    "overall_score": 0.9,
                }
            ]
        }

        # First persistence
        first_result = persist_resources(state)

        first_id = (
            first_result["persisted_resources"][0]["database_id"]
        )

        # Second persistence with the same URL
        second_result = persist_resources(state)

        second_id = (
            second_result["persisted_resources"][0]["database_id"]
        )

        # Same database record must be reused
        assert first_id == second_id

        # Only one database record should exist
        count = (
            db.query(Resource)
            .filter(Resource.url == test_url)
            .count()
        )

        assert count == 1

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