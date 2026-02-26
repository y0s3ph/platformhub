"""Application settings loaded from environment variables."""

from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "PlatformHub"
    debug: bool = False

    database_url: str = "sqlite+aiosqlite:///./platformhub.db"

    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    model_config = {"env_prefix": "PLATFORMHUB_"}


settings = Settings()
