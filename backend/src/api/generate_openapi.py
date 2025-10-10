import json
import os

"""
Utility script to regenerate OpenAPI schema for the FastAPI application.

Writes the schema to interfaces/openapi.json so other containers (e.g. frontend)
can consume the latest API contract.
"""

from src.api.main import app


def main() -> None:
    # Generate OpenAPI schema from the running FastAPI app definition
    openapi_schema = app.openapi()

    # Write to interfaces/openapi.json
    output_dir = "interfaces"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "openapi.json")

    with open(output_path, "w") as f:
        json.dump(openapi_schema, f, indent=2)


if __name__ == "__main__":
    main()
