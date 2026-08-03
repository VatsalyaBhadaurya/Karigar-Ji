from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from supabase import Client

from app.ai.base import BaseTextProvider
from app.dependencies import CurrentUser, get_db, get_text_provider
from app.services.manufacturing_service import ManufacturingService

router = APIRouter(prefix="/manufacturing", tags=["manufacturing"])


class ManufacturingRequest(BaseModel):
    spec_id: str
    project_id: str


@router.post("")
async def generate_manufacturing(
    body: ManufacturingRequest,
    current_user: CurrentUser = None,
    db: Client = Depends(get_db),
    provider: BaseTextProvider = Depends(get_text_provider),
):
    user_id: str = current_user["sub"]
    return await ManufacturingService(provider, db).generate(body.spec_id, body.project_id, user_id)
