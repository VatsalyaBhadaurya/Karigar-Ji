from __future__ import annotations

from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_JWT_SECRET: str = ""
    SUPABASE_STORAGE_BUCKET: str = "karigarji-artifacts"

    # AI: Gemini
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # AI: fal.ai
    FAL_AI_KEY: str = ""
    FAL_FLUX_MODEL: str = "fal-ai/flux-kontext/dev"

    # App
    APP_ENV: Literal["dev", "staging", "prod"] = "dev"
    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_URL: str = "http://localhost:8000"
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "change-me-in-production"

    # Optional
    SENTRY_DSN: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()
