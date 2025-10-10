This folder contains the generated OpenAPI schema for the backend.

To regenerate after code or docs changes:
- From the backend root, run: `python -m src.api.generate_openapi`
This will overwrite interfaces/openapi.json with the latest schema from the running FastAPI app object.

Note: The backend is aligned with FastAPI >=0.111 and Pydantic v2. Ensure your app imports without side effects so schema generation works.
