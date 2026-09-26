import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.categorization.categorization_service import categorize_resource
from app.database.database import SessionLocal
from app.database.models import Resource


def backfill_categories():
    db = SessionLocal()

    try:
        resources = (
            db.query(Resource)
            .filter(Resource.category.is_(None))
            .all()
        )

        print(f"Resources to categorize: {len(resources)}")

        for resource in resources:
            result = categorize_resource(
                metadata={
                    "title": resource.title or "",
                    "resource_type": resource.resource_type or "",
                    "source": resource.source or "",
                    "description": resource.description or "",
                },
                content_snippet=resource.content or "",
            )

            resource.category = result["category"]

            print(
                f"ID {resource.id}: "
                f"{resource.title} -> "
                f"{result['category']} "
                f"(confidence={result['confidence']})"
            )

        db.commit()

        print(f"\nSuccessfully categorized {len(resources)} resources.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    backfill_categories()