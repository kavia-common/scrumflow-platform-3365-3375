# Scrum Mind Backend

FastAPI backend for the Scrum Mind application.

## Quickstart

- Prereqs: Python 3.11+, pip
- Install dependencies:
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

### Quickstart: Jira MCP end-to-end check

Required environment variables (ensure all are set in backend/.env):
- JIRA_BASE_URL
- JIRA_EMAIL
- JIRA_API_TOKEN
- JIRA_PROJECT_KEY
- MCP_CLIENT_CMD

1) Create backend/.env (use .env.example as a template) with valid Jira Cloud credentials and MCP client command.
2) Start the API with uvicorn:
   uvicorn src.api.main:app --reload --host 0.0.0.0 --port 3001
3) Create a Board and a Task, then create/link Jira issue, and finally move the task to trigger Jira transition.

Example script (bash + curl):

# Create a board (if needed)
BOARD_ID=$(curl -s -X POST "http://localhost:3001/boards" \
  -H "Content-Type: application/json" \
  -d '{"name":"Example Project"}' | jq -r '.id')

# Create a task
TASK=$(curl -s -X POST "http://localhost:3001/tasks" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Sync to Jira\",\"board_id\":${BOARD_ID},\"status\":\"todo\"}")
TASK_ID=$(echo "$TASK" | jq -r '.id')

# Create & link Jira issue
LINK=$(curl -s -X POST "http://localhost:3001/integrations/jira/issues" \
  -H "Content-Type: application/json" \
  -d "{\"task_id\":${TASK_ID},\"summary\":\"Sync to Jira\",\"description\":\"Issue created via MCP from Scrum Mind\",\"issue_type\":\"Task\"}")
echo "Link Response: $LINK"
ISSUE_KEY=$(echo "$LINK" | jq -r '.jira_issue_key')

# Verify jira_issue_key on the task
curl -s "http://localhost:3001/tasks/${TASK_ID}" | jq

# Trigger transition by moving the task to in_progress
curl -s -X POST "http://localhost:3001/tasks/${TASK_ID}/move" \
  -H "Content-Type: application/json" \
  -d '{"status":"in_progress"}' | jq

# Or transition directly via integrations API
curl -s -X POST "http://localhost:3001/integrations/jira/issues/${ISSUE_KEY}/transition" \
  -H "Content-Type: application/json" \
  -d '{"status_name":"In Progress"}' | jq

Troubleshooting:
- If you see 503 "Jira integration not configured", re-check all env vars listed above.
- If transitions fail silently, set LOG_LEVEL=DEBUG in .env, restart, and inspect logs for MCP subprocess stderr/stdout decoding issues.
- Ensure MCP_CLIENT_CMD points to an installed client in PATH that supports the tools: createIssue, transitionIssue.

## Environment configuration

The service reads configuration from environment variables (backend/.env). The following are supported.

- DATABASE_URL (required): SQLAlchemy/SQLModel DSN. Defaults to sqlite:///./scrum_mind.db if not set.
- SEED (optional): 1/true/yes/on enables example data seeding when the database is empty.

### Jira MCP Integration variables (required for Jira integration)

Set all of the following to enable Jira integration. If any is missing, the Jira integration endpoints will return 503 and task hooks will be skipped.

- JIRA_BASE_URL: Base URL of your Jira Cloud site (e.g., https://your-domain.atlassian.net).
- JIRA_EMAIL: Jira account email used for API authentication.
- JIRA_API_TOKEN: Jira API token for the above account.
- JIRA_PROJECT_KEY: Project key used when creating new issues (e.g., PROJ).
- MCP_CLIENT_CMD: Command used to invoke the MCP client over stdio (e.g., mcp-jira --stdio). The backend executes this command and sends a JSON payload on stdin.

## How MCP client is invoked

The backend invokes an external MCP client process to perform Jira operations. For each operation, it constructs a JSON payload including the tool name, tool arguments, and Jira context, and then executes MCP_CLIENT_CMD with that payload on stdin. The client is expected to print a JSON response on stdout with a success boolean and optional data.

Example payload structure:
{
  "tool": "createIssue",
  "args": {
    "projectKey": "PROJ",
    "summary": "Title",
    "description": "Desc",
    "issueType": "Task"
  },
  "context": {
    "base_url": "<JIRA_BASE_URL>",
    "email": "<JIRA_EMAIL>",
    "api_token": "<JIRA_API_TOKEN>"
  }
}

Expected response structure:
{
  "success": true,
  "data": {
    "key": "PROJ-123"
  }
}

## Database initialization and seeding

On startup, the application creates tables and, if SEED is true and no data exists yet, it inserts a sample board, sprint, team members, and a few tasks with assorted statuses and story points.

## CORS

CORS is configured to allow http://localhost:3000 for local frontend development.

## REST API overview

- Health: GET /
- Boards: GET /boards; POST /boards
- Sprints: GET /sprints?board_id=...; POST /sprints
- Tasks:
  - GET /tasks?board_id=...
  - POST /tasks
  - PUT /tasks/{id}
  - POST /tasks/{id}/move (UI "review" maps to backend "in_progress")
- Team: GET /team; POST /team
- Progress: GET /progress/summary?board_id=... (returns totals, status counts, and velocity)

## Regenerating OpenAPI spec

Run python -m src.api.generate_openapi to regenerate backend/interfaces/openapi.json.

## Jira MCP Integration

When Jira MCP environment variables are configured, the following endpoints are available and lifecycle hooks are active.

### Endpoints

1) Create and link a Jira issue to a task
- POST /integrations/jira/issues
- Body:
  {
    "task_id": 1,
    "summary": "Title",
    "description": "Desc",
    "issue_type": "Task"
  }
- Behavior: Creates a Jira issue via MCP and persists the returned key into the task's jira_issue_key field.
- Example response:
  {
    "task_id": 1,
    "jira_issue_key": "PROJ-123"
  }

2) Transition a Jira issue
- POST /integrations/jira/issues/{issue_key}/transition
- Body:
  {
    "status_name": "In Progress"
  }
- Behavior: Transitions the given Jira issue via MCP. Returns 200 on success.

### Task lifecycle hook

When moving a task using POST /tasks/{id}/move, if the task has a jira_issue_key and Jira integration is enabled, the backend attempts to transition the linked Jira issue to a status mapped from the internal task status:
- todo -> "To Do"
- in_progress -> "In Progress"
- done -> "Done"
- blocked -> "Blocked"

This is a best-effort operation. Failures are logged and do not block the task update.

## Troubleshooting

- 503 Jira integration not configured:
  Ensure all of JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN, JIRA_PROJECT_KEY, and MCP_CLIENT_CMD are set in backend/.env. Partial configuration disables the integration.
- MCP client not found or fails to execute:
  Confirm MCP_CLIENT_CMD is correct and available on PATH (for example, mcp-jira --stdio). The backend executes this command with shell=True and sends JSON via stdin.
- Empty or invalid MCP response:
  The MCP client must print a single JSON object to stdout. The backend expects success, and optionally data or error. Check backend logs for decoding errors.
- Transitions not happening on task move:
  Verify the task has jira_issue_key set (use GET /tasks/{id}). Also confirm the MCP client supports the transitionIssue tool and that the target status exists in your Jira workflow.
- Permission errors from Jira:
  Ensure the Jira API token belongs to an account with permission to create and transition issues in the target project.

## Verification steps (end-to-end)

1. Prepare .env with all Jira variables and MCP_CLIENT_CMD.
2. Start the backend and create a task via POST /tasks.
3. Create and link a Jira issue via POST /integrations/jira/issues and confirm jira_issue_key is returned.
4. Move the task to in_progress via POST /tasks/{id}/move and verify the Jira issue transitions accordingly.
5. Optionally, call POST /integrations/jira/issues/{issue_key}/transition with "Done" to confirm direct transitions work.

