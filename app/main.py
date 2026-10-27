from pathlib import Path
import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.routing import APIRoute
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field, field_validator

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
from services.quality_config import REVIEW_CONFIDENCE_THRESHOLD
from services.review_queue import get_pending_reviews, review_resource
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
    description=(
        "Academic Resource Intelligence Agent. "
        "Legacy endpoints remain available; API endpoints are also available under /v1."
    ),
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.state.limiter = limiter


class ApiResponse(BaseModel):
    """Flexible response schema that preserves each endpoint's existing payload."""

    model_config = ConfigDict(extra="allow")


class HomeResponse(BaseModel):
    message: str


class HealthResponse(BaseModel):
    status: str
    service: str


async def api_http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    detail = exc.detail
    message = detail if isinstance(detail, str) else "Request failed"
    code_by_status = {
        400: "bad_request",
        401: "unauthorized",
        403: "forbidden",
        404: "not_found",
        405: "method_not_allowed",
        409: "conflict",
        422: "validation_error",
        429: "rate_limit_exceeded",
    }
    code = code_by_status.get(exc.status_code, "http_error")
    logger.warning(
        "HTTP error | method=%s | path=%s | status=%s",
        request.method,
        request.url.path,
        exc.status_code,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {"code": code, "message": message},
            # Keep detail for compatibility with existing clients.
            "detail": jsonable_encoder(detail),
        },
        headers=exc.headers,
    )


async def request_validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    logger.warning(
        "Request validation failed | method=%s | path=%s",
        request.method,
        request.url.path,
    )
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "validation_error",
                "message": "Request validation failed",
            },
            "detail": jsonable_encoder(exc.errors()),
        },
    )


async def rate_limit_exception_handler(
    request: Request,
    exc: RateLimitExceeded,
) -> JSONResponse:
    logger.warning(
        "Rate limit exceeded | method=%s | path=%s",
        request.method,
        request.url.path,
    )
    return JSONResponse(
        status_code=429,
        content={
            "error": {
                "code": "rate_limit_exceeded",
                "message": "Rate limit exceeded",
            },
            "detail": "Rate limit exceeded",
        },
    )


app.add_exception_handler(StarletteHTTPException, api_http_exception_handler)
app.add_exception_handler(
    RequestValidationError,
    request_validation_exception_handler,
)
app.add_exception_handler(
    RateLimitExceeded,
    rate_limit_exception_handler,
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log request metadata and timing without logging credentials or bodies."""
    started_at = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        elapsed_ms = (time.perf_counter() - started_at) * 1000
        logger.exception(
            "Request failed | method=%s | path=%s | duration_ms=%.2f",
            request.method,
            request.url.path,
            elapsed_ms,
        )
        raise

    elapsed_ms = (time.perf_counter() - started_at) * 1000
    logger.info(
        "Request completed | method=%s | path=%s | status=%s | duration_ms=%.2f",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response


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


class ReviewDecision(BaseModel):
    decision: str
    reviewer: str
    comment: str | None = None

    @field_validator("reviewer")
    @classmethod
    def validate_reviewer(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Reviewer cannot be empty")
        return value


@app.get("/", response_model=HomeResponse)
def home():
    logger.info("Home endpoint called")
    return {
        "message": "ISML AI Agent is running"
    }


@app.get("/health", response_model=HealthResponse)
def health():
    logger.info("Health check called")
    return {
        "status": "healthy",
        "service": "ISML AI Agent",
    }


@app.post("/resources", response_model=ApiResponse)
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
            review_confidence=confidence,
            review_status=(
                "PENDING"
                if confidence < REVIEW_CONFIDENCE_THRESHOLD
                else "APPROVED"
            ),
        )

        return {
            "message": "Resource created successfully",
            "id": new_resource.id,
            "title": new_resource.title,
            "url": new_resource.url,
            "category": new_resource.category,
            "confidence": confidence,
            "review_status": new_resource.review_status,
            "overall_score": new_resource.overall_score,
            "created_at": new_resource.created_at,
            "updated_at": new_resource.updated_at,
            "last_verified_at": new_resource.last_verified_at,
            "availability_status": new_resource.availability_status,
        }

    finally:
        db.close()


@app.get("/resources", response_model=list[ApiResponse])
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


@app.get("/resources/search", response_model=ApiResponse)
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


@app.get("/resources/{resource_id}", response_model=ApiResponse)
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


@app.delete("/resources/{resource_id}", response_model=ApiResponse)
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
    user_query: str = Field(
        min_length=1,
        max_length=2000,
        description="Topic or query used to discover academic resources",
    )

    @field_validator("user_query")
    @classmethod
    def validate_user_query(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("user_query cannot be empty")
        return value


@app.post("/api/agent/discover", response_model=ApiResponse)
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
            detail="Agent workflow failed. Please try again later.",
        )


@app.get("/api/quality/governance", response_model=ApiResponse)
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

@app.get("/api/review-queue", response_model=ApiResponse)
@limiter.limit("30/minute")
def list_review_queue(
    request: Request,
    _: bool = Depends(require_api_key),
):
    db = SessionLocal()
    try:
        resources = get_pending_reviews(db)
        return {
            "count": len(resources),
            "items": [
                {
                    "id": item.id,
                    "title": item.title,
                    "url": item.url,
                    "category": item.category,
                    "confidence": item.review_confidence,
                    "status": item.review_status,
                }
                for item in resources
            ],
        }
    finally:
        db.close()


@app.post("/api/review-queue/{resource_id}/decision", response_model=ApiResponse)
@limiter.limit("30/minute")
def decide_resource_review(
    request: Request,
    resource_id: int,
    data: ReviewDecision,
    _: bool = Depends(require_api_key),
):
    db = SessionLocal()
    try:
        item = review_resource(
            db=db,
            resource_id=resource_id,
            decision=data.decision,
            reviewer=data.reviewer,
            comment=data.comment,
        )
        return {
            "message": "Review decision saved",
            "id": item.id,
            "review_status": item.review_status,
            "reviewer": item.reviewed_by,
            "comment": item.review_comment,
            "reviewed_at": item.reviewed_at,
        }
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        db.close()


@app.get("/admin/review", response_class=HTMLResponse)
def admin_review_dashboard():
    dashboard_file = Path(__file__).parent / "templates" / "review_dashboard.html"
    return HTMLResponse(content=dashboard_file.read_text(encoding="utf-8"))


# Register versioned aliases for API routes while preserving existing legacy URLs.
# The admin HTML dashboard and root landing page are intentionally not versioned.
_legacy_api_routes = [
    route
    for route in list(app.routes)
    if isinstance(route, APIRoute)
    and route.path not in {"/", "/admin/review"}
    and not route.path.startswith("/v1/")
]

for _route in _legacy_api_routes:
    app.add_api_route(
        path=f"/v1{_route.path}",
        endpoint=_route.endpoint,
        methods=_route.methods,
        name=f"v1_{_route.name}",
        response_model=_route.response_model,
        status_code=_route.status_code,
        response_class=_route.response_class,
        tags=_route.tags,
        summary=_route.summary,
        description=_route.description,
        responses=_route.responses,
        deprecated=_route.deprecated,
        include_in_schema=True,
    )
