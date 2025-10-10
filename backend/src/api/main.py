from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from src.core.config import settings
from src.db.session import init_db

openapi_tags = [
    {"name": "Health", "description": "Service health and metadata endpoints."},
    {"name": "WebSocket", "description": "Real-time features (reserved)."},
    {"name": "Auth", "description": "Authentication and user account operations."},
    {"name": "Teams", "description": "Team and membership management."},
    {"name": "Boards", "description": "Boards, sprints and tasks management."},
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure DB tables exist on startup
    init_db()
    yield

app = FastAPI(
    title="Scrum Mind Backend",
    description="Backend API for Scrum Mind project management platform.",
    version="0.1.0",
    openapi_tags=openapi_tags,
    lifespan=lifespan,
)

# Configure CORS using environment variable
cors_origins: List[str] = settings.cors_origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins if cors_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Health"], summary="Health Check", description="Returns service health status.")
def health_check():
    """Health check endpoint to verify the service is running."""
    return {"message": "Healthy"}

@app.get(
    "/docs/websocket",
    tags=["WebSocket"],
    summary="WebSocket usage",
    description="Reserved endpoint description for future real-time features. No active WebSocket routes yet."
)
def websocket_usage_note():
    """Provide usage notes for WebSocket capabilities (placeholder)."""
    return {
        "message": "WebSocket endpoints will be documented here when implemented.",
        "note": "No active websocket endpoints yet."
    }
