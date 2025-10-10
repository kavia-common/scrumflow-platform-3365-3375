from functools import lru_cache
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables.

    Env keys:
    - DB_URL (default sqlite:///./scrum_mind.db)
    - JWT_SECRET (default CHANGE_ME; override in production)
    - JWT_EXPIRES_MIN (default 60)
    - JWT_ALGORITHM (default HS256)
    - CORS_ORIGINS (comma-separated; default '*'. Local default set via .env to http://localhost:3000)
    """

    # Database
    db_url: str = Field(default="sqlite:///./scrum_mind.db", alias="DB_URL", description="SQLAlchemy-compatible database URL")

    # Security / JWT
    jwt_secret: str = Field(default="CHANGE_ME", alias="JWT_SECRET", description="Secret key for JWT signing")
    jwt_expires_min: int = Field(default=60, alias="JWT_EXPIRES_MIN", description="JWT expiration time in minutes")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM", description="JWT signing algorithm")

    # CORS
    cors_origins: List[str] = Field(
        default_factory=lambda: ["*"],
        alias="CORS_ORIGINS",
        description="Comma-separated list of allowed CORS origins"
    )

    class Config:
        env_file = ".env"
        case_sensitive = False

    @classmethod
    def parse_cors_origins(cls, value: Optional[str]) -> List[str]:
        if not value:
            return ["*"]
        if isinstance(value, list):
            return value
        return [o.strip() for o in value.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """Create a cached Settings instance."""
    settings = Settings()
    # Normalize cors_origins if provided as a string by environment
    if isinstance(settings.cors_origins, str):
        settings.cors_origins = Settings.parse_cors_origins(settings.cors_origins)
    return settings


# PUBLIC_INTERFACE
def get_db_url() -> str:
    """Return the configured database URL."""
    return get_settings().db_url


# Expose a module-level settings for convenience
settings = get_settings()
