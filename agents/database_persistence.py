from typing import List, Dict, Any

from agents.state import AgentState
from app.database.database import SessionLocal
from services.dedup_service import (
    normalize_url,
    generate_content_hash,
)
from services.resource_repository import (
    create_resource,
    get_resource_by_url,
    get_resource_by_content_hash,
)
from services.logger import log_info, log_error


def persist_resources(state: AgentState) -> AgentState:
    resources = state.get("learning_sequence", [])

    log_info(
        f"Database persistence started | resources_count={len(resources)}"
    )

    persisted_resources: List[Dict[str, Any]] = []

    db = SessionLocal()

    try:
        for item in resources:
            resource = item.get("resource", item)

            title = resource.get("title", "").strip()
            raw_url = resource.get("url", "").strip()
            content = resource.get("content", "")

            if not title or not raw_url:
                continue

            # Normalize URL before database operations
            url = normalize_url(raw_url)

            if not url:
                continue

            # Generate content hash for idempotency
            content_hash = generate_content_hash(content)

            # First check normalized URL
            existing_resource = get_resource_by_url(
                db,
                url
            )

            # If URL is not found, check content hash
            if existing_resource is None and content_hash:
                existing_resource = get_resource_by_content_hash(
                    db,
                    content_hash
                )

            if existing_resource:
                log_info(
                    f"Resource already exists | "
                    f"url={url} | "
                    f"content_hash={content_hash}"
                )

                persisted_resources.append({
                    **item,
                    "database_id": existing_resource.id,
                })

                continue

            scores = item.get("scores", {})

            saved_resource = create_resource(
                db=db,
                title=title,
                url=url,
                resource_type=resource.get(
                    "resource_type",
                    "web"
                ),
                source=resource.get(
                    "source",
                    resource.get(
                        "resource_type",
                        "Web"
                    )
                ),
                category=item.get(
                    "category"
                ),
                tags=item.get(
                    "tags",
                    item.get("keywords", [])
                ),
                description=resource.get(
                    "description",
                    ""
                ),
                content=content,
                content_hash=content_hash,
                relevance_score=scores.get(
                    "relevance"
                ),
                educational_quality=scores.get(
                    "educational_quality"
                ),
                credibility=scores.get(
                    "credibility"
                ),
                learning_effectiveness=scores.get(
                    "learning_effectiveness"
                ),
                overall_score=item.get(
                    "overall_score"
                ),
                processing_status="pending",
            )

            persisted_resources.append({
                **item,
                "database_id": saved_resource.id,
            })

        log_info(
            f"Database persistence completed | "
            f"saved_count={len(persisted_resources)}"
        )

        return {
            **state,
            "persisted_resources": persisted_resources,
        }

    except Exception as e:
        db.rollback()

        log_error(
            f"Database persistence failed | error={e}"
        )
        raise

    finally:
        db.close()
