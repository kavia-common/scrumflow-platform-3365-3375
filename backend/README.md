# Backend (FastAPI) - Dependencies and Notes

This backend uses FastAPI with Pydantic v2.

## Installing dependencies

Create and activate a virtual environment, then install:

```
pip install -r requirements.txt
```

Run the app (example):

```
uvicorn src.main:app --reload --host 0.0.0.0 --port 3001
```

Note: Adjust the module path (src.main:app) to match your entrypoint if different.

## Dependency versions

- fastapi >= 0.111,<1.0 (compatible with Pydantic v2)
- pydantic >= 2.7,<3.0
- starlette >= 0.37,<1.0
- uvicorn >= 0.30,<1.0
- pydantic-settings >= 2.3,<3.0
- python-multipart for form parsing
- email-validator for EmailStr support
- passlib[bcrypt] and python-jose[cryptography] for auth flows
- SQLAlchemy 2.x and Alembic for persistence (if used)

## Pydantic v2 migration tips

If upgrading from Pydantic v1:
- Replace from pydantic import BaseSettings usage with pydantic_settings.BaseSettings.
- Validators:
  - Old: @validator("field") -> New: @field_validator("field") (from pydantic import field_validator)
  - Root validators: @root_validator(pre/post=...) -> @model_validator(mode="before"/"after")
- Parsing:
  - BaseModel.parse_obj(...) -> Model.model_validate(obj)
  - BaseModel.parse_raw(...) -> Model.model_validate_json(json_str)
- Exporting:
  - model.dict() -> model.model_dump()
  - model.json() -> model.model_dump_json()
- Config:
  - class Config: ... -> class Config: ... or use model_config = ConfigDict(...)
  - validate_assignment, arbitrary_types_allowed etc. move to ConfigDict

For FastAPI:
- Response models still use Pydantic models transparently.
- OAuth2PasswordRequestForm still requires form-encoded data (`application/x-www-form-urlencoded`).

## OpenAPI schema generation

This repo includes an `interfaces` folder for the OpenAPI schema. To (re)generate:

1. Ensure the app imports without running (no side-effect execution on import).
2. Start the app or load the FastAPI app object in a script.
3. Export to `interfaces/openapi.json`.

Example (pseudo):

```python
# src/api/generate_openapi.py
from src.main import app
from pathlib import Path
import json

schema = app.openapi()
Path("backend/interfaces").mkdir(parents=True, exist_ok=True)
Path("backend/interfaces/openapi.json").write_text(json.dumps(schema, indent=2))
```

Then run:

```
python -m src.api.generate_openapi
```

Adjust paths according to your project structure.
