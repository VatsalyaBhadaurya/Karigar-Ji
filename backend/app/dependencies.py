from __future__ import annotations

import logging
from functools import lru_cache
from typing import Annotated

import httpx
from fastapi import Depends, Header
from jose import JWTError, jwt
from supabase import Client

from app.ai.base import BaseVisionProvider, BaseRenderProvider, BaseTextProvider
from app.ai.prompt_loader import render_prompt
from app.ai.providers.gemini import GeminiProvider
from app.ai.providers.huggingface import HuggingFaceRenderProvider
from app.config import settings
from app.db.client import get_supabase
from app.exceptions import UnauthorizedError

logger = logging.getLogger(__name__)


# ── Database ────────────────────────────────────────────────
def get_db() -> Client:
    return get_supabase()


# ── Auth ────────────────────────────────────────────────────
@lru_cache(maxsize=1)
def _get_jwks() -> dict:
    """Fetch and cache Supabase's JWKS for ES256 token verification."""
    url = f"{settings.SUPABASE_URL}/auth/v1/.well-known/jwks.json"
    resp = httpx.get(url, timeout=10.0)
    resp.raise_for_status()
    return resp.json()


def get_current_user(authorization: Annotated[str | None, Header()] = None) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthorizedError()
    token = authorization.removeprefix("Bearer ")

    # Try ES256 via JWKS (new Supabase auth — default since 2024)
    try:
        jwks = _get_jwks()
        payload = jwt.decode(
            token,
            jwks,
            algorithms=["ES256", "RS256"],
            options={"verify_aud": False},
        )
        return payload
    except JWTError:
        pass

    # Fallback: HS256 with the project JWT secret (legacy / self-hosted)
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
    return HuggingFaceRenderProvider(hf_token=settings.HF_TOKEN, model=settings.HF_FLUX_MODEL)
