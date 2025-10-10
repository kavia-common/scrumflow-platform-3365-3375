from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .dependencies import init_db_and_seed
from .routers import boards, sprints, tasks, teams, progress
from .routers import integrations_jira

# OpenAPI tag definitions for grouping endpoints in docs
openapi_tags = [
    {"name": "Boards", "description": "Manage boards"},
    {"name": "Sprints", "description": "Manage sprints"},
    {"name": "Tasks", "description": "Manage tasks and movements"},
    {"name": "Team", "description": "Manage team members"},
    {"name": "Progress", "description": "Progress and metrics"},
    {"name": "Health", "description": "Service health checks"},
    {"name": "Integrations - Jira", "description": "Jira integration via MCP client"},
]

# PUBLIC_INTERFACE
app = FastAPI(
    title="Scrum Mind API",
    description="Backend API for Scrum Mind application",
    version="0.1.0",
    openapi_tags=openapi_tags,
)

# CORS: allow frontend at localhost:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """
    Initialize database and optionally seed dev data based on SEED env var.

    This ensures SQLite/SQLModel tables are created before handling requests.
    """
    init_db_and_seed()


# PUBLIC_INTERFACE
@app.get(
    "/",
    tags=["Health"],
    summary="Health Check",
    description="API health check endpoint.",
    responses={200: {"description": "Service is healthy"}},
)
def health_check():
    """
    Health check endpoint.

    Returns:
        JSON object confirming service health.
    """
    return {"message": "Healthy"}


# Include routers grouped by tags
app.include_router(boards.router)
app.include_router(sprints.router)
app.include_router(tasks.router)
app.include_router(teams.router)
app.include_router(progress.router)
app.include_router(integrations_jira.router)
