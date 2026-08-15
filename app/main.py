import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.database.init_db import init_db
from app.database.database import SessionLocal
from services.resource_repository import (
    create_resource,
    get_all_resources,
    get_resource_by_id,
    delete_resource,
)


# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# FastAPI application
app = FastAPI(
    title="ISML AI Agent",
    description="Academic Resource Intelligence Agent",
    version="1.0.0"
)


# Initialize database
init_db()


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Resource request model
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


# Root endpoint
@app.get("/")
def home():
    logger.info("Home endpoint called")
    return {
        "message": "ISML AI Agent is running"
    }


# Health endpoint
@app.get("/health")
def health():
    logger.info("Health check called")
    return {
        "status": "healthy",
        "service": "ISML AI Agent"
    }


# Create resource
@app.post("/resources")
def add_resource(resource: ResourceCreate):
    db = SessionLocal()

    try:
        new_resource = create_resource(
            db=db,
            title=resource.title,
            url=resource.url,
            resource_type=resource.resource_type,
            source=resource.source,
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
            "overall_score": new_resource.overall_score,
        }

    finally:
        db.close()


# Get all resources
@app.get("/resources")
def list_resources():
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
                "description": resource.description,
                "overall_score": resource.overall_score,
            }
            for resource in resources
        ]

    finally:
        db.close()


# Get resource by ID
@app.get("/resources/{resource_id}")
def get_resource(resource_id: int):
    db = SessionLocal()

    try:
        resource = get_resource_by_id(db, resource_id)

        if resource is None:
            raise HTTPException(
                status_code=404,
                detail="Resource not found"
            )

        return {
            "id": resource.id,
            "title": resource.title,
            "url": resource.url,
            "resource_type": resource.resource_type,
            "source": resource.source,
            "description": resource.description,
            "content": resource.content,
            "relevance_score": resource.relevance_score,
            "educational_quality": resource.educational_quality,
            "credibility": resource.credibility,
            "learning_effectiveness": resource.learning_effectiveness,
            "overall_score": resource.overall_score,
            "created_at": resource.created_at,
        }

    finally:
        db.close()


# Delete resource
@app.delete("/resources/{resource_id}")
def remove_resource(resource_id: int):
    db = SessionLocal()

    try:
        deleted = delete_resource(db, resource_id)

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Resource not found"
            )

        return {
            "message": "Resource deleted successfully",
            "id": resource_id,
        }

    finally:
        db.close()