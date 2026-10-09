from sqlalchemy.orm import Session

from app.database.models import Resource, ResourceLifecycleEvent


ALLOWED_TRANSITIONS = {
    "DISCOVERED": {"VALIDATED"},
    "VALIDATED": {"EVALUATED"},
    "EVALUATED": {"APPROVED", "REJECTED"},
    "APPROVED": {"ARCHIVED", "UNAVAILABLE"},
    "REJECTED": {"ARCHIVED", "UNAVAILABLE"},
    "ARCHIVED": set(),
    "UNAVAILABLE": set(),
}


def transition_resource_status(
    db: Session,
    resource_id: int,
    new_status: str,
    note: str | None = None,
) -> Resource:
    new_status = new_status.strip().upper()

    if new_status not in ALLOWED_TRANSITIONS:
        raise ValueError(f"Invalid lifecycle status: {new_status}")

    resource = db.get(Resource, resource_id)

    if resource is None:
        raise LookupError(f"Resource {resource_id} not found")

    old_status = resource.status

    if new_status not in ALLOWED_TRANSITIONS[old_status]:
        raise ValueError(
            f"Invalid transition: {old_status} -> {new_status}"
        )

    try:
        event = ResourceLifecycleEvent(
            resource_id=resource.id,
            from_status=old_status,
            to_status=new_status,
            note=note,
        )

        resource.status = new_status
        db.add(event)
        db.commit()
        db.refresh(resource)

        return resource

    except Exception:
        db.rollback()
        raise


def get_resource_lifecycle_history(
    db: Session,
    resource_id: int,
) -> list[ResourceLifecycleEvent]:
    resource = db.get(Resource, resource_id)

    if resource is None:
        raise LookupError(f"Resource {resource_id} not found")

    return (
        db.query(ResourceLifecycleEvent)
        .filter(ResourceLifecycleEvent.resource_id == resource_id)
        .order_by(ResourceLifecycleEvent.changed_at.asc())
        .all()
    )
