from __future__ import annotations

import logging
from typing import Annotated

from fastapi import Depends, Header
from jose import JWTError, jwt
from supabase import Client

from app.ai.base import BaseVisionProvider, BaseRenderProvider, BaseTextProvider
from app.ai.prompt_loader import render_prompt
from app.ai.providers.gemini import GeminiProvider
from app.ai.providers.fal_ai import FalAiProvider
from app.config import settings
from app.db.client import get_supabase
from app.exceptions import UnauthorizedError

logger = logging.getLogger(__name__)


# ── Database ────────────────────────────────────────────────
def get_db() -> Client:
    return get_supabase()


# ── Auth ────────────────────────────────────────────────────
def get_current_user(authorization: Annotated[str | None, Header()] = None) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthorizedError()
    token = authorization.removeprefix("Bearer ")
    try:
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )
        return payload
    except JWTError as exc:
        logger.warning("JWT decode failed: %s", exc)
        raise UnauthorizedError() from exc


CurrentUser = Annotated[dict, Depends(get_current_user)]
DB = Annotated[Client, Depends(get_db)]


# ── AI providers ─────────────────────────────────────────────
def get_vision_provider() -> BaseVisionProvider:
    return GeminiProvider(api_key=settings.GEMINI_API_KEY, model=settings.GEMINI_MODEL)


def get_text_provider() -> BaseTextProvider:
    return GeminiProvider(api_key=settings.GEMINI_API_KEY, model=settings.GEMINI_MODEL)


def get_render_provider() -> BaseRenderProvider:
    return FalAiProvider(api_key=settings.FAL_AI_KEY, model=settings.FAL_FLUX_MODEL)
