from fastapi import APIRouter

from app.api.v1 import upload, vision, render, techpack, manufacturing, trend, pattern, export, project

router = APIRouter()

router.include_router(upload.router)
router.include_router(vision.router)
router.include_router(render.router)
router.include_router(techpack.router)
router.include_router(manufacturing.router)
router.include_router(trend.router)
router.include_router(pattern.router)
router.include_router(export.router)
router.include_router(project.router)
