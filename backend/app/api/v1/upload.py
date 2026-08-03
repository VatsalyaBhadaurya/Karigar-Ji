from __future__ import annotations

import uuid

from fastapi import APIRouter, UploadFile, File, Form, Depends
from supabase import Client

from app.dependencies import CurrentUser, get_db
from app.services.storage_service import StorageService

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("")
async def upload_sketch(
    file: UploadFile = File(...),
    project_id: str = Form(...),
    current_user: CurrentUser = None,
    db: Client = Depends(get_db),
):
    user_id: str = current_user["sub"]
    file_bytes = await file.read()
    mime_type = file.content_type or "image/jpeg"

    storage_svc = StorageService(db)
    storage_path, public_url = storage_svc.upload_sketch(
        file_bytes=file_bytes,
        file_name=file.filename or "sketch",
        mime_type=mime_type,
        user_id=user_id,
        project_id=project_id,
    )

    upload_id = str(uuid.uuid4())
    result = db.table("uploads").insert({
        "id": upload_id,
        "project_id": project_id,
        "user_id": user_id,
        "storage_path": storage_path,
        "public_url": public_url,
        "file_name": file.filename or "sketch",
        "file_size": len(file_bytes),
        "mime_type": mime_type,
        "upload_status": "complete",
    }).execute()

    db.table("projects").update({"status": "analyzing"}).eq("id", project_id).execute()

    return result.data[0]
