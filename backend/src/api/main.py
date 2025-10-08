from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .dependencies import init_db_and_seed
from .routers import boards, sprints, tasks, teams, progress

openapi_tags = [
    {"name": "Boards", "description": "Manage boards"},
    {"name": "Sprints", "description": "Manage sprints"},
    {"name": "Tasks", "description": "Manage tasks and movements"},
    {"name": "Team", "description": "Manage team members"},
    {"name": "Progress", "description": "Progress and metrics"},
]

app = FastAPI(
    title="Scrum Mind API",
    description="Backend API for Scrum Mind application",
    version="0.1.0",
    openapi_tags=openapi_tags,
)

# Restrict CORS to frontend default localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """Initialize database and optionally seed dev data."""
    init_db_and_seed()


@app.get("/", tags=["Health"], summary="Health Check", description="API health check endpoint.")
def health_check():
    return {"message": "Healthy"}


# Include routers
app.include_router(boards.router)
app.include_router(sprints.router)
app.include_router(tasks.router)
app.include_router(teams.router)
app.include_router(progress.router)
