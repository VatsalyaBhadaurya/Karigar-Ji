from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from supabase import Client

from app.dependencies import CurrentUser, get_db
from app.exceptions import NotFoundError, ForbiddenError

router = APIRouter(prefix="/project", tags=["project"])


class CreateProjectRequest(BaseModel):
    name: str
    description: str = ""


class UpdateProjectRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None


@router.post("")
def create_project(
    body: CreateProjectRequest,
    current_user: CurrentUser = None,
    db: Client = Depends(get_db),
):
    user_id: str = current_user["sub"]
    result = db.table("projects").insert({
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "name": body.name,
        "description": body.description,
        "status": "draft",
    }).execute()
    return result.data[0]


@router.get("")
def list_projects(
    current_user: CurrentUser = None,
    db: Client = Depends(get_db),
):
    user_id: str = current_user["sub"]
    result = (
        db.table("projects")
        .select("*")
        .eq("user_id", user_id)
        .order("updated_at", desc=True)
        .execute()
    )
    return result.data


@router.get("/{project_id}")
def get_project(
    project_id: str,
    current_user: CurrentUser = None,
    db: Client = Depends(get_db),
):
    user_id: str = current_user["sub"]
    result = (
        db.table("projects")
        .select("""
            *,
            uploads(id, public_url, file_name, upload_status),
            garment_specs(id, spec_json, garment_type, silhouette, is_current, version),
            renders(id, view_type, public_url, render_status),
            techpacks(id, pdf_url, pack_status),
            manufacturing_docs(id, doc_status),
            trend_reports(id, report_status),
            patterns(id, piece_name, pattern_status)
        """)
        .eq("id", project_id)
        .single()
        .execute()
    )
    if not result.data:
        raise NotFoundError("Project", project_id)
    if result.data["user_id"] != user_id:
        raise ForbiddenError()
    return result.data


@router.patch("/{project_id}")
def update_project(
    project_id: str,
    body: UpdateProjectRequest,
    current_user: CurrentUser = None,
    db: Client = Depends(get_db),
):
    user_id: str = current_user["sub"]
    updates = body.model_dump(exclude_none=True)
    if not updates:
        raise NotFoundError("Project", project_id)
    result = (
        db.table("projects")
        .update(updates)
        .eq("id", project_id)
        .eq("user_id", user_id)
        .execute()
    )
    if not result.data:
        raise NotFoundError("Project", project_id)
    return result.data[0]


@router.delete("/{project_id}")
def delete_project(
    project_id: str,
    current_user: CurrentUser = None,
    db: Client = Depends(get_db),
):
    user_id: str = current_user["sub"]
    db.table("projects").delete().eq("id", project_id).eq("user_id", user_id).execute()
    return {"deleted": project_id}
