from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from supabase import Client

from app.dependencies import CurrentUser, get_db
from app.services.pattern_engine import PatternEngineService
from app.services.storage_service import StorageService

router = APIRouter(prefix="/pattern", tags=["pattern"])


class PatternRequest(BaseModel):
    spec_id: str
    project_id: str
    sizes: list[str] = ["S", "M", "L"]


@router.post("")
def generate_pattern(
    body: PatternRequest,
    current_user: CurrentUser = None,
    db: Client = Depends(get_db),
):
    user_id: str = current_user["sub"]
    svc = PatternEngineService(StorageService(db), db)
    return svc.generate(body.spec_id, body.project_id, user_id, body.sizes)
