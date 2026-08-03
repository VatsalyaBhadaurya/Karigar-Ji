from __future__ import annotations

from fastapi import APIRouter, Depends, BackgroundTasks
from pydantic import BaseModel
from supabase import Client

from app.ai.base import BaseRenderProvider
from app.dependencies import CurrentUser, get_db, get_render_provider
from app.services.render_service import RenderService
from app.services.storage_service import StorageService

router = APIRouter(prefix="/render", tags=["render"])

DEFAULT_VIEWS = ["front", "back", "side_left", "studio_3q"]


class RenderRequest(BaseModel):
    spec_id: str
    project_id: str
    views: list[str] = DEFAULT_VIEWS


@router.post("")
async def create_renders(
    body: RenderRequest,
    background_tasks: BackgroundTasks,
    current_user: CurrentUser = None,
    db: Client = Depends(get_db),
    provider: BaseRenderProvider = Depends(get_render_provider),
):
    user_id: str = current_user["sub"]
    storage_svc = StorageService(db)
    svc = RenderService(provider, storage_svc, db)

    jobs = svc.create_render_jobs(body.spec_id, body.project_id, user_id, body.views)

    for job in jobs:
        background_tasks.add_task(svc.generate_render, job["id"], user_id)

    return {"renders": jobs, "message": f"{len(jobs)} render(s) queued"}


@router.get("/{render_id}")
def get_render(
    render_id: str,
    current_user: CurrentUser = None,
    db: Client = Depends(get_db),
    provider: BaseRenderProvider = Depends(get_render_provider),
):
    user_id: str = current_user["sub"]
    storage_svc = StorageService(db)
    return RenderService(provider, storage_svc, db).get_render(render_id, user_id)
