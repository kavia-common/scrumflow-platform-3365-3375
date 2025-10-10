# Scrum Mind Backend

FastAPI backend for the Scrum Mind application.

Quickstart
- Prereqs: Python 3.11+, pip
- Install:
  - pip install -r requirements.txt
- Environment (.env in backend/):
  - DATABASE_URL=sqlite:///./scrum_mind.db
  - SEED=true   # optional; seeds sample data on startup
- Start (dev, port 3001):
  - uvicorn src.api.main:app --reload --host 0.0.0.0 --port 3001
- Docs:
  - Swagger: http://localhost:3001/docs
  - OpenAPI: http://localhost:3001/openapi.json

Environment configuration
- DATABASE_URL (required): SQLAlchemy/SQLModel DSN. Defaults to sqlite:///./scrum_mind.db if not set.
- SEED (optional): 1/true/yes/on enables example data seeding when DB is empty.

Database initialization and seeding
- On startup, `init_db_and_seed()` creates tables and, if SEED is true and no data exists, inserts:
  - One example board, one active sprint, example team members, and a few tasks with various statuses and story points.

CORS
- Configured to allow http://localhost:3000 (frontend dev origin).

Smoke-test checklist (end-to-end)
- Health: GET /
- Boards: GET /boards; POST /boards
- Sprints: GET /sprints?board_id=...; POST /sprints
- Tasks:
  - GET /tasks?board_id=...
  - POST /tasks
  - PUT /tasks/{id}
  - POST /tasks/{id}/move (UI "review" -> backend "in_progress")
- Team: GET /team; POST /team
- Progress: GET /progress/summary?board_id=... (check totals and velocity)

Regenerating OpenAPI spec
- python -m src.api.generate_openapi -> backend/interfaces/openapi.json
