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
    GEMINI_MODEL: str = "gemini-flash-latest"

    # AI: HuggingFace (FLUX.1-Kontext-dev)
    HF_TOKEN: str = ""
    HF_FLUX_MODEL: str = "black-forest-labs/FLUX.1-schnell"

    # App
    APP_ENV: Literal["dev", "staging", "prod"] = "dev"
    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_URL: str = "http://localhost:8000"
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "change-me-in-production"

    # Dev helpers
    USE_MOCK_AI: bool = False  # set true to bypass Gemini in local dev

    # Optional
    SENTRY_DSN: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()
