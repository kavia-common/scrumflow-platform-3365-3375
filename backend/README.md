# Scrum Mind Backend

FastAPI backend for the Scrum Mind application.

Quickstart
- Prereqs: Python 3.11+, pip
- Install:
  - pip install -r requirements.txt
- Environment (.env in backend/):
  - DATABASE_URL=sqlite:///./scrum_mind.db
  - SEED=true   # optional; seeds sample data on startup
  - JIRA_BASE_URL=https://your-domain.atlassian.net            # Jira Cloud base URL
  - JIRA_EMAIL=you@example.com                                 # Jira account email
  - JIRA_API_TOKEN=your_jira_api_token                         # Jira API token (create in Atlassian)
  - JIRA_PROJECT_KEY=PROJ                                      # Jira project key for new issues
  - MCP_CLIENT_CMD="mcp-jira --stdio"                          # MCP client command to execute
- Start (dev, port 3001):
  - uvicorn src.api.main:app --reload --host 0.0.0.0 --port 3001
- Docs:
  - Swagger: http://localhost:3001/docs
  - OpenAPI: http://localhost:3001/openapi.json

Environment configuration
- DATABASE_URL (required): SQLAlchemy/SQLModel DSN. Defaults to sqlite:///./scrum_mind.db if not set.
- SEED (optional): 1/true/yes/on enables example data seeding when DB is empty.
- Jira MCP (optional): if configured, Jira integration endpoints and hooks are enabled.
  - JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN, JIRA_PROJECT_KEY, MCP_CLIENT_CMD must all be set.

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

Jira MCP Integration (optional)
- Configure env vars in backend/.env (see backend/.env.example).
- When enabled, the backend exposes:
  - POST /integrations/jira/issues
      Body: { "task_id": 1, "summary": "Title", "description": "Desc", "issue_type": "Task" }
      Effect: Creates a Jira issue via MCP and stores jira_issue_key on the task.
  - POST /integrations/jira/issues/{issue_key}/transition
      Body: { "status_name": "In Progress" }
      Effect: Transitions the Jira issue via MCP.
- Task hooks:
  - POST /tasks/{id}/move will attempt to transition linked Jira issue to a mapped status (To Do, In Progress, Done, Blocked).
- Resilience:
  - If MCP client is unavailable or env vars are missing, integration is skipped with logs; existing endpoints continue to work.
