import pytest

from app.database.database import SessionLocal
from app.database.models import Resource
from services.resource_repository import create_resource


@pytest.mark.parametrize(
    ("confidence", "expected_status"),
    [
        (0.69, "PENDING"),
        (0.70, "APPROVED"),
        (None, "PENDING"),
    ],
)
def test_review_status_confidence_threshold(
    confidence,
    expected_status,
    monkeypatch,
):
    url = f"https://example.com/enh012-threshold-{confidence}"

    # Keep this unit test independent of external URL checks.
    monkeypatch.setattr(
        "services.resource_repository.check_resource_availability",
        lambda _url: "available",
    )

    db = SessionLocal()

    try:
        existing = (
            db.query(Resource)
            .filter(Resource.url == url)
            .first()
        )
        if existing:
            db.delete(existing)
            db.commit()

        saved = create_resource(
            db=db,
            title="ENH-012 Confidence Threshold Test",
            url=url,
            resource_type="web",
            source="Example",
            review_confidence=confidence,
        )

        assert saved.review_status == expected_status
        assert saved.review_confidence == confidence

    finally:
        existing = (
            db.query(Resource)
            .filter(Resource.url == url)
            .first()
        )
        if existing:
            db.delete(existing)
            db.commit()

        db.close()
