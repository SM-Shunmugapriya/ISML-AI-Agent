from typing import List

from agents.state import AgentState
from services.embedding_service import generate_embedding as _generate_embedding, generate_embeddings_batch
from services.logger import log_info, log_error

from app.database.database import SessionLocal
from app.database.models import Resource


def generate_resource_embeddings(state: AgentState) -> AgentState:
    resources = state.get("persisted_resources", [])

    log_info(
        f"Embedding generation started | resources_count={len(resources)}"
    )

    embeddings: List[List[float]] = []
    valid_items = []
    texts = []

    db = SessionLocal()

    try:
        # Collect valid resources without changing their original order.
        for item in resources:
            resource = item.get("resource", item)

            title = resource.get("title", "")
            description = resource.get("description", "")
            content = resource.get("content", "")
            database_id = item.get("database_id")

            text = f"{title}\n{description}\n{content}".strip()

            if not text:
                log_info(
                    f"Skipping embedding | title={title} | reason=empty_text"
                )
                continue

            if not database_id:
                log_info(
                    f"Skipping embedding | title={title} | "
                    "reason=missing_database_id"
                )
                continue

            valid_items.append(
                {
                    "database_id": database_id,
                    "title": title,
                }
            )
            texts.append(text)

        # Generate vectors in batches of up to 50 texts per API request.
        if texts:
            embeddings = generate_embeddings_batch(texts, batch_size=50)

            if len(embeddings) != len(valid_items):
                raise ValueError(
                    "Embedding count does not match valid resource count"
                )

        # Update database rows using their exact IDs.
        for item, embedding in zip(valid_items, embeddings):
            db_resource = (
                db.query(Resource)
                .filter(Resource.id == item["database_id"])
                .first()
            )

            if db_resource:
                db_resource.embedding = embedding
                db_resource.processing_status = "completed"

                log_info(
                    f"Embedding saved to database | "
                    f"id={db_resource.id} | "
                    f"title={db_resource.title} | "
                    f"dimensions={len(embedding)}"
                )
            else:
                log_info(
                    f"Database resource not found | "
                    f"id={item['database_id']}"
                )

        db.commit()

        log_info(
            f"Embedding generation completed | "
            f"embeddings_count={len(embeddings)}"
        )

        return {
            **state,
            "embeddings": embeddings,
        }

    except Exception as e:
        db.rollback()

        log_error(f"Embedding generation failed | error={e}")

        return {
            **state,
            "embeddings": embeddings,
        }

    finally:
        db.close()


def generate_embedding(text: str) -> list[float]:
    """Compatibility wrapper for existing callers and tests."""
    return _generate_embedding(text)
