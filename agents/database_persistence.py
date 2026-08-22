from typing import List, Dict, Any

from agents.state import AgentState
from app.database.database import SessionLocal
from services.resource_repository import (
    create_resource,
    get_resource_by_url,
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
            url = resource.get("url", "").strip()

            if not title or not url:
                continue

            # Check whether resource already exists
            existing_resource = get_resource_by_url(
                db,
                url
            )

            if existing_resource:
                log_info(
                    f"Resource already exists | url={url}"
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
                description=resource.get(
                    "description",
                    ""
                ),
                content=resource.get(
                    "content",
                    ""
                ),
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
            )

            persisted_resources.append({
                **item,
                "database_id": saved_resource.id,
            })

        log_info(
            f"Database persistence completed | saved_count={len(persisted_resources)}"
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