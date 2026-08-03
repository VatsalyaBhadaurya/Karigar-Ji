from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from supabase import Client

from app.dependencies import CurrentUser, get_db
from app.services.export_service import ExportService
from app.services.storage_service import StorageService

router = APIRouter(prefix="/export", tags=["export"])


class ExportRequest(BaseModel):
    project_id: str
    export_type: str = "zip"
    include: list[str] = ["renders", "techpack", "patterns", "flats"]


@router.post("")
async def create_export(
    body: ExportRequest,
    current_user: CurrentUser = None,
    db: Client = Depends(get_db),
):
    user_id: str = current_user["sub"]
    return await ExportService(StorageService(db), db).create_export(
        project_id=body.project_id,
        user_id=user_id,
        export_type=body.export_type,
        include=body.include,
    )
