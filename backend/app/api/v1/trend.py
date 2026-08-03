from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from supabase import Client

from app.ai.base import BaseTextProvider
from app.dependencies import CurrentUser, get_db, get_text_provider
from app.services.trend_service import TrendService

router = APIRouter(prefix="/trend", tags=["trend"])


class TrendRequest(BaseModel):
    spec_id: str
    project_id: str


@router.post("")
async def generate_trend(
    body: TrendRequest,
    current_user: CurrentUser = None,
    db: Client = Depends(get_db),
    provider: BaseTextProvider = Depends(get_text_provider),
):
    user_id: str = current_user["sub"]
    return await TrendService(provider, db).generate(body.spec_id, body.project_id, user_id)
