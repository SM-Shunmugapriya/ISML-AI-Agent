from collections import Counter

from sqlalchemy.orm import Session

from app.database.models import Resource
from services.quality_config import get_quality_level, is_auto_approved


def get_quality_distribution(db: Session) -> dict:
    """Return quality governance distribution for stored resources."""

    resources = (
        db.query(Resource)
        .filter(Resource.overall_score.is_not(None))
        .all()
    )

    levels = Counter()
    approved_count = 0
    review_count = 0

    for resource in resources:
        score = float(resource.overall_score)
        level = get_quality_level(score)

        levels[level] += 1

        if is_auto_approved(score):
            approved_count += 1
        else:
            review_count += 1

    total = len(resources)

    distribution = {}
    for level in [
        "Excellent",
        "High Quality",
        "Acceptable",
        "Review/Reject",
    ]:
        count = levels[level]
        percentage = round((count / total) * 100, 2) if total else 0.0

        distribution[level] = {
            "count": count,
            "percentage": percentage,
        }

    return {
        "total_resources": total,
        "auto_approved": approved_count,
        "review_required": review_count,
        "distribution": distribution,
    }
