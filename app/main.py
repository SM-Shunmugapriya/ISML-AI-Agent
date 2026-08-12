import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# FastAPI application
app = FastAPI(
    title="ISML AI Agent",
    description="Academic Resource Intelligence Agent",
    version="1.0.0"
)


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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