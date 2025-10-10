# Scrum Mind Backend

FastAPI backend for the Scrum Mind application.

## Environment configuration

This backend loads configuration from a `.env` file (via python-dotenv). The following variables are supported:

- `DATABASE_URL` (required): SQLAlchemy/SQLModel database connection string.
  - Default (if not set): `sqlite:///./scrum_mind.db` (SQLite file in the backend working directory).
- `SEED` (optional): Enables seeding of development/sample data on startup.
  - Truthy values: `1`, `true`, `yes`, `on` (case-insensitive). Any other value is treated as false.
  - Default (if not set): `false`.

Example `.env` (already provided in this repo under `backend/.env`):

```
DATABASE_URL=sqlite:///./scrum_mind.db
SEED=true
```

## Database initialization and seeding

On application startup, the app calls `init_db_and_seed()` (see `src/api/dependencies.py`):

- Creates all tables defined in SQLModel metadata if they do not exist.
- If `SEED` is enabled, inserts example data (a sample board, sprint, team members, and tasks) unless data already exists.

This ensures the API is immediately usable in development environments.

## Running locally

1. Ensure Python dependencies are installed:
   ```
   pip install -r requirements.txt
   ```
2. Verify or adjust the `.env` file in `backend/`.
3. Start the server:
   ```
   uvicorn src.api.main:app --reload --host 0.0.0.0 --port 3001
   ```
4. Open API docs:
   - Swagger UI: http://localhost:3001/docs
   - OpenAPI JSON: http://localhost:3001/openapi.json

## Regenerating OpenAPI spec

To export the current OpenAPI schema to `interfaces/openapi.json` for consumers:
```
python -m src.api.generate_openapi
```
