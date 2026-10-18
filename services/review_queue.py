from datetime import datetime

from sqlalchemy.orm import Session

from app.database.models import Resource


def get_pending_reviews(db: Session) -> list[Resource]:
    """Return resources waiting for human review."""
    return (
        db.query(Resource)
        .filter(Resource.review_status == "PENDING")
        .order_by(Resource.id.asc())
        .all()
    )


def review_resource(
    db: Session,
    resource_id: int,
    decision: str,
    reviewer: str,
    comment: str | None = None,
) -> Resource:
    """Approve or reject a pending resource with reviewer details."""
    decision = decision.strip().upper()

    if decision not in {"APPROVED", "REJECTED"}:
        raise ValueError("Decision must be APPROVED or REJECTED")

    resource = db.get(Resource, resource_id)
    if resource is None:
        raise LookupError(f"Resource {resource_id} not found")

    if resource.review_status != "PENDING":
        raise ValueError(
            f"Resource is not pending review: {resource.review_status}"
        )

    try:
        resource.review_status = decision
        resource.review_comment = comment
        resource.reviewed_by = reviewer
        resource.reviewed_at = datetime.utcnow()
        db.commit()
        db.refresh(resource)
        return resource
    except Exception:
        db.rollback()
        raise
