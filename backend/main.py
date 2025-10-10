"""
FastAPI application entrypoint.

This file exposes the FastAPI app instance for the preview system (uvicorn)
to auto-discover and serve on port 3001. It imports the application defined
under src.api.main and re-exports it as `app`.

Usage:
- The preview system will run: uvicorn main:app --port 3001
- Swagger UI: /docs
- OpenAPI JSON: /openapi.json
"""

from src.api.main import app  # re-export the existing app instance

# Avoid "imported but unused" linter warning by explicitly exposing in __all__
__all__ = ["app"]

# Note:
# Do not hardcode host/port here. The preview/deployment system controls runtime settings.
# If you need to run locally:
#   uvicorn main:app --reload --port 3001
