# Backend

This backend is implemented with FastAPI and exposes a REST API for the Scrum Mind platform. It ships with interactive documentation via Swagger UI and an OpenAPI schema for client generation.

## Introduction and Overview

The API supports core scrum features including authentication, teams, boards, sprints, and tasks. Endpoints are grouped with tags and are discoverable through the integrated Swagger UI. The application instance is exposed as `main:app` for the preview system to serve automatically.

## Getting Started (Preview system notes)

The preview environment auto-starts the backend; no manual start commands are required. Use the base URLs below to explore the API and documentation. If you run locally for development, avoid hardcoding host/port as these are controlled by the runtime; examples assume port `3001`.

## Base URL and Ports

- Base URL (local preview): http://localhost:3001
- Default port: 3001

All paths documented below are relative to the base URL.

## Swagger UI and OpenAPI JSON

- Swagger UI: http://localhost:3001/docs
- OpenAPI JSON: http://localhost:3001/openapi.json

You can use the OpenAPI JSON with tools like OpenAPI Generator or Swagger Codegen to create client SDKs. An export helper is also provided to save the current schema to `interfaces/openapi.json`:
- From backend root: `python -m src.api.generate_openapi`

## Authentication

Currently, the root health endpoint is public. All business endpoints under `/api` typically require Bearer tokens issued by the Auth endpoints using OAuth2 password flow.
- Scheme: Bearer JWT (`Authorization: Bearer <token>`)
- Token acquisition: `POST /api/auth/login`
- Future note: JWT/OAuth enhancements may be introduced (e.g., refresh tokens, OAuth providers). Refer to the Auth tag in Swagger for the latest details.

## Endpoints

### Health

- GET `/`
  - Summary: Health Check
  - Description: Returns service health status.
  - Example request:
    ```bash
    curl -s http://localhost:3001/
    ```
  - Example response:
    ```json
    { "message": "Healthy" }
    ```
  - Status codes:
    - 200 OK: Service is healthy.

- GET `/docs/websocket`
  - Summary: WebSocket usage (placeholder)
  - Description: Notes about future real-time features. No active WebSocket routes yet.

### Auth

- POST `/api/auth/register` — Create a new user account.
- POST `/api/auth/login` — Obtain a JWT access token via OAuth2 password flow.
- GET `/api/auth/me` — Get the current authenticated user’s profile.

See Swagger UI for request/response schemas.

### Teams

- POST `/api/teams` — Create a team.
- GET `/api/teams` — List teams.
- GET `/api/teams/{team_id}` — Get team by id.

### Boards

- POST `/api/boards` — Create a board under a team.
- GET `/api/boards/team/{team_id}` — List boards for a team.
- GET `/api/boards/{board_id}` — Get board by id.

### Sprints

- POST `/api/sprints` — Create a sprint on a board.
- GET `/api/sprints/board/{board_id}` — List sprints by board.
- GET `/api/sprints/{sprint_id}` — Get sprint by id.

### Tasks

- POST `/api/tasks` — Create a task.
- GET `/api/tasks/board/{board_id}` — List tasks for a board with optional filters.
- GET `/api/tasks/{task_id}` — Get task by id.
- PATCH `/api/tasks/{task_id}/status` — Update task status.

### Future placeholders

- `/sprints`: Additional operations such as updating sprint date ranges or closing sprints may be added in future sprints.
- `/tasks`: Extended operations such as bulk updates, comments, and attachments may be introduced later.

## Error Handling and Status Codes

The API uses conventional HTTP status codes to indicate success or failure:
- 200 OK: Successful retrieval or operation.
- 201 Created: Resource created.
- 400 Bad Request: Invalid input or validation failure.
- 401 Unauthorized: Missing or invalid authentication.
- 403 Forbidden: Authenticated but not permitted to perform the operation.
- 404 Not Found: Resource not found.
- 422 Unprocessable Entity: Request validation error (schema mismatch).
- 500 Internal Server Error: Unexpected condition.

Error responses follow FastAPI’s standard structure with detail messages. Example:
```json
{
  "detail": "Not authorized to create board for this team"
}
```

## Versioning

- API version: `0.1.0` (see OpenAPI info and `src/api/main.py`).
- Semantic versioning will be used as the API evolves. Breaking changes will increment the major version, and non-breaking additions will increment the minor version.

## Changelog

- 0.1.0
  - Initial endpoints: health, auth, teams, boards, sprints, tasks.
  - Swagger UI and OpenAPI schema available at `/docs` and `/openapi.json`.

## Linting and Formatting

This backend uses Ruff for linting and formatting, with configuration in `pyproject.toml`.

Common commands:
- `make lint`        # Run Ruff checks
- `make lint-fix`    # Run Ruff with autofix
- `make format`      # Format code with Ruff formatter
