"""Backend configuration from environment variables."""

import os
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # Database
    database_url: str = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:root@localhost:3306/saarturnier"
    )

    # JWT
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = environment != "production"

    # API
    api_title: str = "saarTURNier API"
    api_version: str = "1.0.0"

    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = False


settings = Settings()
