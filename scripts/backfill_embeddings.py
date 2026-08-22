import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.database.database import SessionLocal
from app.database.models import Resource
from services.embedding_service import generate_embedding


def backfill_embeddings():
    db = SessionLocal()

    try:
        resources = (
            db.query(Resource)
            .filter(Resource.embedding.is_(None))
            .all()
        )

        print(f"Resources without embeddings: {len(resources)}")

        success_count = 0
        failed_count = 0

        for index, resource in enumerate(resources, start=1):
            text = "\n".join(
                [
                    resource.title or "",
                    resource.description or "",
                    resource.content or "",
                ]
            ).strip()

            if not text:
                print(
                    f"[{index}/{len(resources)}] SKIPPED: "
                    f"{resource.title}"
                )
                continue

            try:
                embedding = generate_embedding(text)

                if not embedding:
                    print(
                        f"[{index}/{len(resources)}] FAILED: "
                        f"Empty embedding | {resource.title}"
                    )
                    failed_count += 1
                    continue

                resource.embedding = embedding

                db.commit()

                success_count += 1

                print(
                    f"[{index}/{len(resources)}] SAVED: "
                    f"{resource.title} | dimensions={len(embedding)}"
                )

            except Exception as e:
                db.rollback()
                failed_count += 1

                print(
                    f"[{index}/{len(resources)}] ERROR: "
                    f"{resource.title} | {e}"
                )

        total = db.query(Resource).count()

        embedded = (
            db.query(Resource)
            .filter(Resource.embedding.is_not(None))
            .count()
        )

        missing = (
            db.query(Resource)
            .filter(Resource.embedding.is_(None))
            .count()
        )

        print("\n========== BACKFILL COMPLETED ==========")
        print(f"TOTAL RESOURCES: {total}")
        print(f"SUCCESSFULLY SAVED: {success_count}")
        print(f"FAILED: {failed_count}")
        print(f"EMBEDDINGS SAVED: {embedded}")
        print(f"WITHOUT EMBEDDING: {missing}")

    finally:
        db.close()


if __name__ == "__main__":
    backfill_embeddings()