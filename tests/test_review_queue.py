from app.database.database import SessionLocal
from app.database.models import Resource
from services.review_queue import get_pending_reviews, review_resource


def test_review_queue_approve_with_comment():
    db = SessionLocal()
    url = "https://example.com/enh012-approve-test"

    try:
        existing = db.query(Resource).filter(Resource.url == url).first()
        if existing:
            db.delete(existing)
            db.commit()

        item = Resource(
            title="Review Queue Approval Test",
            url=url,
            resource_type="web",
            source="Example",
            review_status="PENDING",
            review_confidence=0.45,
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        resource_id = item.id

        result = review_resource(
            db, resource_id, "APPROVED", "Test Reviewer",
            "Content verified",
        )

        assert result.review_status == "APPROVED"
        assert result.reviewed_by == "Test Reviewer"
        assert result.review_comment == "Content verified"
        assert result.reviewed_at is not None

    finally:
        item = db.query(Resource).filter(Resource.url == url).first()
        if item:
            db.delete(item)
            db.commit()
        db.close()


def test_review_queue_reject_with_comment():
    db = SessionLocal()
    url = "https://example.com/enh012-reject-test"

    try:
        existing = db.query(Resource).filter(Resource.url == url).first()
        if existing:
            db.delete(existing)
            db.commit()

        item = Resource(
            title="Review Queue Rejection Test",
            url=url,
            resource_type="web",
            source="Example",
            review_status="PENDING",
            review_confidence=0.30,
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        resource_id = item.id

        result = review_resource(
            db, resource_id, "REJECTED", "Test Reviewer",
            "Insufficient educational value",
        )

        assert result.review_status == "REJECTED"
        assert result.review_comment == "Insufficient educational value"

    finally:
        item = db.query(Resource).filter(Resource.url == url).first()
        if item:
            db.delete(item)
            db.commit()
        db.close()


def test_review_queue_returns_only_pending_resources():
    db = SessionLocal()
    url = "https://example.com/enh012-pending-test"

    try:
        existing = db.query(Resource).filter(Resource.url == url).first()
        if existing:
            db.delete(existing)
            db.commit()

        item = Resource(
            title="Pending Queue Test",
            url=url,
            resource_type="web",
            source="Example",
            review_status="PENDING",
            review_confidence=0.50,
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        resource_id = item.id

        pending = get_pending_reviews(db)

        assert any(resource.id == resource_id for resource in pending)

    finally:
        item = db.query(Resource).filter(Resource.url == url).first()
        if item:
            db.delete(item)
            db.commit()
        db.close()
