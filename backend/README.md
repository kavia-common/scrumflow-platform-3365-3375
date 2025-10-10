# Backend

This backend is implemented with FastAPI and provides interactive API documentation.

## Run and Access

- App entrypoint: `main:app`
- Default port (preview system): `3001`
- Swagger UI: `http://localhost:3001/docs`
- OpenAPI JSON: `http://localhost:3001/openapi.json`
- Health check: `GET http://localhost:3001/` returns `{"message": "Healthy"}`

Local run example:
- Install dependencies:
  - `pip install -r requirements.txt`
- Start server (do not hardcode host/port; example uses 3001):
  - `uvicorn main:app --reload --port 3001`

## Linting and Formatting

This backend uses Ruff (linter + formatter) and Black configuration via pyproject.toml.

Common commands:
- `make lint`        # Run Ruff checks
- `make lint-fix`    # Run Ruff with autofix
- `make format`      # Format code with Ruff formatter

You need Python 3.9+ and the following tools installed in your environment:
- ruff
- black (config provided, though formatting is handled by ruff format)

Install Ruff:
  `pip install ruff`

Optional (Black):
  `pip install black`

## Regenerate OpenAPI schema (optional)

To export the OpenAPI schema to `interfaces/openapi.json`:
- From backend root: `python -m src.api.generate_openapi`
