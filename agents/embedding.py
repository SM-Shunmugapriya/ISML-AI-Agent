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
            url = resource.get("url", "")

            text = f"{title}\n{description}\n{content}".strip()

            if not text:
                log_info(
                    f"Skipping embedding | title={title} | reason=empty_text"
                )
                continue

            # Generate embedding
            embedding = generate_embedding(text)

            embeddings.append(embedding)

            # Find corresponding database resource
            db_resource = None

            if url:
                db_resource = (
                    db.query(Resource)
                    .filter(Resource.url == url)
                    .first()
                )

            # Save embedding into database
            if db_resource:
                db_resource.embedding = embedding

                log_info(
                    f"Embedding saved to database | "
                    f"title={db_resource.title} | "
                    f"dimensions={len(embedding)}"
                )
            else:
                log_info(
                    f"Database resource not found | url={url}"
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