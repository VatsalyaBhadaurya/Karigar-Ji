from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from supabase import Client

from app.ai.base import BaseVisionProvider
from app.dependencies import CurrentUser, get_db, get_vision_provider
from app.services.vision_service import VisionService

router = APIRouter(prefix="/vision", tags=["vision"])


class AnalyzeRequest(BaseModel):
    upload_id: str
    project_id: str
    user_notes: str = ""


class SpecUpdateRequest(BaseModel):
    spec_json: dict | None = None
    garment_type: str | None = None
    silhouette: str | None = None


@router.post("/analyze")
async def analyze_sketch(
    body: AnalyzeRequest,
    current_user: CurrentUser = None,
    db: Client = Depends(get_db),
    provider: BaseVisionProvider = Depends(get_vision_provider),
):
    user_id: str = current_user["sub"]
    svc = VisionService(provider, db)
    return await svc.analyze_sketch(body.upload_id, body.project_id, user_id, body.user_notes)


@router.get("/spec/{spec_id}")
def get_spec(
    spec_id: str,
    current_user: CurrentUser = None,
    db: Client = Depends(get_db),
    provider: BaseVisionProvider = Depends(get_vision_provider),
):
    user_id: str = current_user["sub"]
    return VisionService(provider, db).get_spec(spec_id, user_id)


@router.patch("/spec/{spec_id}")
def update_spec(
    spec_id: str,
    body: SpecUpdateRequest,
    current_user: CurrentUser = None,
    db: Client = Depends(get_db),
    provider: BaseVisionProvider = Depends(get_vision_provider),
):
    user_id: str = current_user["sub"]
    updates = body.model_dump(exclude_none=True)
    return VisionService(provider, db).update_spec(spec_id, user_id, updates)
