from datetime import datetime
from requests import RequestException
import requests

from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.database.models import Resource
from app.security.url_validator import validate_external_url


REQUEST_TIMEOUT = 10
MAX_RESOURCES_PER_RUN = 100


def check_resource_availability(url: str) -> str:
    """Check an external URL without following unvalidated redirects."""
    try:
        if not validate_external_url(url):
            return "unavailable"

        response = requests.get(
            url,
            timeout=REQUEST_TIMEOUT,
            allow_redirects=False,
            stream=True,
            headers={"User-Agent": "ISML-Resource-Freshness-Checker/1.0"},
        )

        try:
            if 200 <= response.status_code < 400:
                return "available"
            return "unavailable"
        finally:
            response.close()

    except (RequestException, ValueError, OSError):
        return "unavailable"


def verify_resource(db: Session, resource: Resource) -> Resource:
    """Verify one resource and update its freshness fields."""
    resource.availability_status = check_resource_availability(resource.url)
    resource.last_verified_at = datetime.utcnow()
    db.commit()
    db.refresh(resource)
    return resource


def verify_top_resources(limit: int = MAX_RESOURCES_PER_RUN) -> dict:
    """Verify up to 100 resources, prioritizing never-verified/old resources."""
    checked = 0
    available = 0
    unavailable = 0

    db = SessionLocal()
    try:
        resources = (
            db.query(Resource)
            .order_by(
                Resource.last_verified_at.asc().nullsfirst(),
                Resource.id.asc(),
            )
            .limit(min(max(limit, 1), MAX_RESOURCES_PER_RUN))
            .all()
        )

        for resource in resources:
            try:
                verify_resource(db, resource)
                checked += 1
                if resource.availability_status == "available":
                    available += 1
                else:
                    unavailable += 1
            except Exception:
                db.rollback()
                print(f"Freshness verification failed for resource ID {resource.id}")

        return {
            "checked": checked,
            "available": available,
            "unavailable": unavailable,
        }
    finally:
        db.close()
