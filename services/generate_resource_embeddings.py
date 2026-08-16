from app.database.database import SessionLocal
from app.database.models import Resource
from services.embedding_service import generate_embedding


def generate_resource_embeddings():
    db = SessionLocal()

    try:
        resources = (
            db.query(Resource)
            .filter(Resource.embedding.is_(None))
            .all()
        )

        print(f"Resources without embeddings: {len(resources)}")

        for resource in resources:
            text = f"{resource.title}\n{resource.description or ''}\n{resource.content or ''}"

            print(f"Generating embedding for: {resource.title}")

            embedding = generate_embedding(text)

            resource.embedding = embedding

            print(
                f"Embedding generated: {len(embedding)} dimensions"
            )

        db.commit()

        print("All resource embeddings saved successfully.")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    generate_resource_embeddings()
    