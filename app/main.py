import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from app.database.init_db import init_db
from app.database.database import SessionLocal
from app.security.auth import require_api_key
from app.security.url_validator import validate_external_url

from services.resource_repository import (
    create_resource,
    get_all_resources,
    get_resource_by_id,
    delete_resource,
    search_similar_resources,
)

from services.embedding_service import generate_embedding
from app.categorization.categorization_service import categorize_resource
from services.observability_service import ObservabilityService
from services.quality_dashboard import get_quality_distribution
from services.freshness_scheduler import (
    start_freshness_scheduler,
    stop_freshness_scheduler,
)

from agents.workflow import app as agent_workflow


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="ISML AI Agent",
    description="Academic Resource Intelligence Agent",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)

init_db()




app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ResourceCreate(BaseModel):
    title: str
    url: str
    resource_type: str
    source: str
    description: str | None = None
    content: str | None = None
    relevance_score: float | None = None
    educational_quality: float | None = None
    credibility: float | None = None
    learning_effectiveness: float | None = None
    overall_score: float | None = None

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        if not validate_external_url(value):
            raise ValueError("Invalid or unsafe external URL")
        return value


@app.get("/")
def home():
    logger.info("Home endpoint called")
    return {
        "message": "ISML AI Agent is running"
    }


@app.get("/health")
def health():
    logger.info("Health check called")
    return {
        "status": "healthy",
        "service": "ISML AI Agent",
    }


@app.post("/resources")
@limiter.limit("30/minute")
def add_resource(
    request: Request,
    resource: ResourceCreate,
    _: bool = Depends(require_api_key),
):
    db = SessionLocal()

    try:
        category_result = categorize_resource(
            metadata={
                "title": resource.title,
                "resource_type": resource.resource_type,
                "source": resource.source,
                "description": resource.description or "",
            },
            content_snippet=resource.content or "",
        )

        category = category_result["category"]
        confidence = category_result["confidence"]

        new_resource = create_resource(
            db=db,
            title=resource.title,
            url=resource.url,
            resource_type=resource.resource_type,
            source=resource.source,
            category=category,
            description=resource.description,
            content=resource.content,
            relevance_score=resource.relevance_score,
            educational_quality=resource.educational_quality,
            credibility=resource.credibility,
            learning_effectiveness=resource.learning_effectiveness,
            overall_score=resource.overall_score,
        )

        return {
            "message": "Resource created successfully",
            "id": new_resource.id,
            "title": new_resource.title,
            "url": new_resource.url,
            "category": new_resource.category,
            "confidence": confidence,
            "overall_score": new_resource.overall_score,
            "created_at": new_resource.created_at,
            "updated_at": new_resource.updated_at,
            "last_verified_at": new_resource.last_verified_at,
            "availability_status": new_resource.availability_status,
        }

    finally:
        db.close()


@app.get("/resources")
@limiter.limit("30/minute")
def list_resources(
    request: Request,
    _: bool = Depends(require_api_key),
):
    db = SessionLocal()

    try:
        resources = get_all_resources(db)

        return [
            {
                "id": resource.id,
                "title": resource.title,
                "url": resource.url,
                "resource_type": resource.resource_type,
                "source": resource.source,
                "category": resource.category,
                "description": resource.description,
                "overall_score": resource.overall_score,
                "created_at": resource.created_at,
                "updated_at": resource.updated_at,
                "last_verified_at": resource.last_verified_at,
                "availability_status": resource.availability_status,
            }
            for resource in resources
        ]

    finally:
        db.close()


@app.get("/resources/search")
@limiter.limit("30/minute")
def search_resources(
    request: Request,
    query: str,
    limit: int = 5,
    _: bool = Depends(require_api_key),
):
    db = SessionLocal()

    try:
        if not query.strip():
            raise HTTPException(
                status_code=400,
                detail="Query cannot be empty",
            )

        if limit < 1 or limit > 20:
            raise HTTPException(
                status_code=400,
                detail="Limit must be between 1 and 20",
            )

        query_embedding = generate_embedding(query)

        results = search_similar_resources(
            db=db,
            query_embedding=query_embedding,
            limit=limit,
        )

        return {
            "query": query,
            "count": len(results),
            "results": [
                {
                    "id": resource.id,
                    "title": resource.title,
                    "url": resource.url,
                    "resource_type": resource.resource_type,
                    "source": resource.source,
                    "category": resource.category,
                    "description": resource.description,
                    "created_at": resource.created_at,
                    "updated_at": resource.updated_at,
                    "last_verified_at": resource.last_verified_at,
                    "availability_status": resource.availability_status,
                    "similarity_distance": round(
                        float(distance), 4
                    ),
                }
                for resource, distance in results
            ],
        }

    finally:
        db.close()


@app.get("/resources/{resource_id}")
@limiter.limit("30/minute")
def get_resource(
    request: Request,
    resource_id: int,
    _: bool = Depends(require_api_key),
):
    db = SessionLocal()

    try:
        resource = get_resource_by_id(db, resource_id)

        if resource is None:
            raise HTTPException(
                status_code=404,
                detail="Resource not found",
            )

        return {
            "id": resource.id,
            "title": resource.title,
            "url": resource.url,
            "resource_type": resource.resource_type,
            "source": resource.source,
            "category": resource.category,
            "description": resource.description,
            "content": resource.content,
            "relevance_score": resource.relevance_score,
            "educational_quality": resource.educational_quality,
            "credibility": resource.credibility,
            "learning_effectiveness": resource.learning_effectiveness,
            "overall_score": resource.overall_score,
            "created_at": resource.created_at,
            "updated_at": resource.updated_at,
            "last_verified_at": resource.last_verified_at,
            "availability_status": resource.availability_status,
        }

    finally:
        db.close()


@app.delete("/resources/{resource_id}")
@limiter.limit("30/minute")
def remove_resource(
    request: Request,
    resource_id: int,
    _: bool = Depends(require_api_key),
):
    db = SessionLocal()

    try:
        deleted = delete_resource(db, resource_id)

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Resource not found",
            )

        return {
            "message": "Resource deleted successfully",
            "id": resource_id,
        }

    finally:
        db.close()


class AgentDiscoverRequest(BaseModel):
    user_query: str


@app.post("/api/agent/discover")
@limiter.limit("10/minute")
def discover_agent(
    request: Request,
    request_data: AgentDiscoverRequest,
    _: bool = Depends(require_api_key),
):
    observability = ObservabilityService()

    try:
        run_id = observability.start_run(
            input_data=request_data.user_query
        )

        result = agent_workflow.invoke(
            {"user_query": request_data.user_query}
        )

        observability.record_counts(
            search_count=result.get("search_count", 0),
            discovered_count=len(result.get("resources", [])),
            valid_count=result.get("valid_count", 0),
            evaluated_count=result.get("evaluated_count", 0),
            ranked_count=result.get("ranked_count", 0),
            stored_count=result.get("stored_count", 0),
        )

        summary = observability.finish_run(
            status="success"
        )

        logger.info(
            f"Workflow completed | run_id={run_id} | "
            f"duration={summary['duration_seconds']}s"
        )

        return result.get("validated_output", result)

    except Exception as e:
        logger.exception("Agent workflow execution failed")

        observability.record_error(
            stage="workflow",
            error=e,
        )

        observability.finish_run(status="failed")

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@app.get("/api/quality/governance")
@limiter.limit("30/minute")
def quality_governance(
    request: Request,
    _: bool = Depends(require_api_key),
):
    db = SessionLocal()

    try:
        return get_quality_distribution(db)

    finally:
        db.close()