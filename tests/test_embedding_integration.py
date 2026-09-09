from agents.database_persistence import persist_resources
from agents.embedding import generate_resource_embeddings
from app.database.database import SessionLocal
from app.database.models import Resource


def test_embedding_pipeline_integration():
    test_url = "https://example.com/bug-013-test"

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
                    "title": "Python Embedding Test",
                    "url": test_url,
                    "resource_type": "web",
                    "source": "Example",
                    "category": "Practice",
                    "keywords": ["python", "embedding", "testing"],
                    "description": "Test resource for embedding integration.",
                    "content": "Python embedding integration test content.",
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

        # Step 1: Persist resource
        persisted_state = persist_resources(state)

        assert len(persisted_state["persisted_resources"]) == 1

        # Step 2: Generate and save embedding
        embedding_state = generate_resource_embeddings(persisted_state)

        assert len(embedding_state["embeddings"]) == 1
        assert len(embedding_state["embeddings"][0]) == 3072

        # Step 3: Verify embedding exists in database
        saved = (
            db.query(Resource)
            .filter(Resource.url == test_url)
            .first()
        )

        assert saved is not None
        assert saved.embedding is not None
        assert len(saved.embedding) == 3072

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