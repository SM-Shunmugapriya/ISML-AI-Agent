from app.database.database import SessionLocal
from services.embedding_service import generate_embedding
from services.resource_repository import search_similar_resources


def find_similar_resources(query: str, limit: int = 5):
    """
    Search resources using vector similarity.
    """

    if not query or not query.strip():
        raise ValueError("Query cannot be empty")

    # Generate embedding for the user's query
    query_embedding = generate_embedding(query)

    db = SessionLocal()

    try:
        # Use repository function for database search
        results = search_similar_resources(
            db=db,
            query_embedding=query_embedding,
            limit=limit
        )

        return [
            {
                "id": resource.id,
                "title": resource.title,
                "url": resource.url,
                "resource_type": resource.resource_type,
                "source": resource.source,
                "similarity_score": round(1 - distance, 4),
            }
            for resource, distance in results
        ]

    finally:
        db.close()


if __name__ == "__main__":
    query = input("Enter your learning query: ")

    results = find_similar_resources(query)

    print("\nSimilar Resources:\n")

    for result in results:
        print(f"Title: {result['title']}")
        print(f"URL: {result['url']}")
        print(f"Type: {result['resource_type']}")
        print(f"Source: {result['source']}")
        print(f"Similarity: {result['similarity_score']}")
        print("-" * 60)