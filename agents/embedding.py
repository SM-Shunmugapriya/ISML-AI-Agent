from typing import List

from agents.state import AgentState
from services.embedding_service import generate_embedding
from services.logger import log_info, log_error

from app.database.database import SessionLocal
from app.database.models import Resource


def generate_resource_embeddings(state: AgentState) -> AgentState:
    resources = state.get("persisted_resources", [])

    log_info(
        f"Embedding generation started | resources_count={len(resources)}"
    )

    embeddings: List[List[float]] = []

    db = SessionLocal()

    try:
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
                    f"reason=missing_database_id"
                )
                continue

            # Generate embedding
            embedding = generate_embedding(text)

            embeddings.append(embedding)

            # Find exact persisted database resource by ID
            db_resource = (
                db.query(Resource)
                .filter(Resource.id == database_id)
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
                    f"id={database_id}"
                )

        # Commit all embedding updates
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

        log_error(
            f"Embedding generation failed | error={e}"
        )

        return {
            **state,
            "embeddings": embeddings,
        }

    finally:
        db.close()