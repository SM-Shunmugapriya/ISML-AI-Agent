from sqlalchemy.orm import Session

from app.database.models import Resource


def create_resource(
    db: Session,
    title: str,
    url: str,
    resource_type: str,
    source: str,
    description: str | None = None,
    content: str | None = None,
    relevance_score: float | None = None,
    educational_quality: float | None = None,
    credibility: float | None = None,
    learning_effectiveness: float | None = None,
    overall_score: float | None = None,
):
    resource = Resource(
        title=title,
        url=url,
        resource_type=resource_type,
        source=source,
        description=description,
        content=content,
        relevance_score=relevance_score,
        educational_quality=educational_quality,
        credibility=credibility,
        learning_effectiveness=learning_effectiveness,
        overall_score=overall_score,
    )

    db.add(resource)
    db.commit()
    db.refresh(resource)

    return resource


def get_resource_by_id(
    db: Session,
    resource_id: int
):
    return (
        db.query(Resource)
        .filter(Resource.id == resource_id)
        .first()
    )


def get_resource_by_url(
    db: Session,
    url: str
):
    return (
        db.query(Resource)
        .filter(Resource.url == url)
        .first()
    )


def get_all_resources(
    db: Session
):
    return db.query(Resource).all()


def delete_resource(
    db: Session,
    resource_id: int
):
    resource = get_resource_by_id(db, resource_id)

    if resource is None:
        return False

    db.delete(resource)
    db.commit()

    return True


def search_similar_resources(
    db: Session,
    query_embedding: list[float],
    limit: int = 5
):
    """
    Find resources most similar to the query embedding
    using cosine similarity.
    """

    distance = Resource.embedding.cosine_distance(query_embedding)

    results = (
        db.query(
            Resource,
            distance.label("distance")
        )
        .filter(Resource.embedding.is_not(None))
        .order_by(distance)
        .limit(limit)
        .all()
    )

    return results