# Scrum Mind Backend (FastAPI)

FastAPI backend providing boards, sprints, tasks, team, and progress endpoints.

Quickstart
- Prereqs: Python 3.11+, pip
- Install deps:
  - cd backend
  - pip install -r requirements.txt
- Environment (.env in backend/):
  - DATABASE_URL=sqlite:///./scrum_mind.db
  - SEED=true   # optional; seeds example data on startup
- Start (port 3001):
  - uvicorn src.api.main:app --reload --host 0.0.0.0 --port 3001
- API docs:
  - Swagger: http://localhost:3001/docs
  - OpenAPI JSON: http://localhost:3001/openapi.json

Environment variables
- DATABASE_URL (required): SQLAlchemy/SQLModel DSN (default sqlite:///./scrum_mind.db if omitted).
- SEED (optional): 1/true/yes/on enables seeding example data if database empty.

CORS
- Preconfigured to allow http://localhost:3000 (frontend dev server).

Seeding
- With SEED=true, startup creates tables and inserts sample board, sprint, team, and tasks if DB is empty.

Smoke-test checklist (API)
- Health: GET / -> 200 { "message": "Healthy" }
- Boards:
  - GET /boards -> list
  - POST /boards {name} -> 201
- Sprints:
  - GET /sprints?board_id=... -> list
  - POST /sprints {...} -> 201
- Tasks:
  - GET /tasks?board_id=... -> list
  - POST /tasks {...} -> 201
  - PUT /tasks/{id} -> 200
  - POST /tasks/{id}/move {status, sprint_id?, board_id?} -> 200
    - Note: frontend UI "review" maps to backend "in_progress"
- Team:
  - GET /team -> list
  - POST /team {...} -> 201
- Progress:
  - GET /progress/summary?board_id=... -> totals, by-status, velocity (sum story_points of done)

Dev notes
- Regenerate OpenAPI: python -m src.api.generate_openapi (writes to backend/interfaces/openapi.json)
- Tests: pytest (uses in-memory sqlite and dependency override)