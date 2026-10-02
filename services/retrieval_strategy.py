from typing import List, Dict, Any, Tuple

from app.database.database import SessionLocal
from app.database.models import Resource
from services.vector_search import find_similar_resources
from services.logger import log_info, log_error


SIMILARITY_THRESHOLD = 0.65
QUALITY_THRESHOLD = 0.70
MIN_HIGH_QUALITY_RESOURCES = 3


def _normalize_quality_score(score: Any) -> float:
    """
    Normalize stored quality scores to 0.0-1.0.

    Existing database records may contain scores either as:
    - 0.0-1.0
    - 0-100
    """
    if score is None:
        return 0.0

    try:
        value = float(score)
    except (TypeError, ValueError):
        return 0.0

    if value > 1.0:
        return value / 100.0

    return value


def check_existing_knowledge(
    query: str,
    limit: int = 10,
) -> Tuple[bool, List[Dict[str, Any]]]:
    """
    Check whether existing vector knowledge is sufficient
    before starting external resource discovery.

    Returns:
        (is_sufficient, matching_resources)
    """

    if not query or not query.strip():
        raise ValueError("Query cannot be empty")

    log_info(
        f"Knowledge retrieval check started | "
        f"query={query} | limit={limit}"
    )

    try:
        similar_resources = find_similar_resources(
            query,
            limit=limit,
        )

        if not similar_resources:
            log_info(
                "Knowledge retrieval insufficient | "
                "reason=no_similar_resources"
            )
            return False, []

        resource_ids = [
            item["id"]
            for item in similar_resources
            if item.get("id") is not None
        ]

        db = SessionLocal()

        try:
            db_resources = (
                db.query(Resource)
                .filter(Resource.id.in_(resource_ids))
                .all()
            )

            resources_by_id = {
                resource.id: resource
                for resource in db_resources
            }

            matching_resources: List[Dict[str, Any]] = []

            for item in similar_resources:
                resource = resources_by_id.get(item.get("id"))

                if resource is None:
                    continue

                similarity = float(
                    item.get("similarity_score", 0.0)
                )

                quality_score = _normalize_quality_score(
                    resource.overall_score
                )

                if (
                    similarity >= SIMILARITY_THRESHOLD
                    and quality_score >= QUALITY_THRESHOLD
                ):
                    matching_resources.append({
                        "id": resource.id,
                        "title": resource.title,
                        "url": resource.url,
                        "content": resource.content or "",
                        "resource_type": resource.resource_type,
                        "type": resource.resource_type,
                        "source": resource.source,
                        "category": resource.category or "Supplementary",
                        "tags": resource.tags or [],
                        "description": resource.description or "",
                        "summary": resource.description or "",
                        "keywords": resource.tags or [],
                        "difficulty": "beginner",
                        "scores": {
                            "relevance": _normalize_quality_score(
                                resource.relevance_score
                            ),
                            "educational_quality": _normalize_quality_score(
                                resource.educational_quality
                            ),
                            "credibility": _normalize_quality_score(
                                resource.credibility
                            ),
                            "learning_effectiveness": _normalize_quality_score(
                                resource.learning_effectiveness
                            ),
                        },
                        "overall_score": quality_score,
                        "similarity_score": similarity,
                        "database_id": resource.id,
                    })

        finally:
            db.close()

        is_sufficient = (
            len(matching_resources)
            >= MIN_HIGH_QUALITY_RESOURCES
        )

        log_info(
            f"Knowledge retrieval completed | "
            f"similar_count={len(similar_resources)} | "
            f"high_quality_count={len(matching_resources)} | "
            f"coverage_sufficient={is_sufficient}"
        )

        return is_sufficient, matching_resources

    except Exception as e:
        log_error(
            f"Knowledge retrieval failed | error={e}"
        )
        raise


def retrieve_existing_knowledge(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node that checks existing knowledge before discovery.

    A retrieval hit skips external discovery. If retrieval is
    insufficient or fails, the normal discovery path is used.
    """

    query = (
        state.get("topic")
        or state.get("user_query")
        or ""
    )

    try:
        is_sufficient, resources = check_existing_knowledge(
            query=query,
            limit=10,
        )

        if is_sufficient:
            log_info(
                f"Knowledge retrieval hit | "
                f"coverage={len(resources)} | "
                f"discovery_required=False"
            )

            return {
                **state,
                "retrieval_hit": True,
                "retrieved_resources": resources,
                "topic": query,
                "retrieval_coverage": len(resources),
                "resources": resources,
                "evaluated_resources": resources,
                "ranked_resources": resources,
                "categorized_resources": resources,
                "persisted_resources": [],
                "embeddings": [],
            }

        log_info(
            "Knowledge retrieval miss | "
            "discovery_required=True"
        )

        return {
            **state,
            "retrieval_hit": False,
            "retrieved_resources": [],
            "retrieval_coverage": len(resources),
        }

    except Exception as e:
        log_error(
            f"Knowledge retrieval node failed | "
            f"falling back to discovery | error={e}"
        )

        return {
            **state,
            "retrieval_hit": False,
            "retrieved_resources": [],
            "retrieval_coverage": 0,
        }
