from __future__ import annotations

import base64
import logging
import time
import uuid

import httpx
from supabase import Client

from app.ai.base import BaseRenderProvider
from app.ai.prompt_loader import render_prompt
from app.exceptions import NotFoundError
from app.services.storage_service import StorageService

logger = logging.getLogger(__name__)

VIEW_TYPES = ["front", "back", "side_left", "studio_3q"]


def _decode_render_result(result: str) -> tuple[bytes, str]:
    """
    Render providers may return either:
    - A data URL:  "data:image/jpeg;base64,<b64>"  (HuggingFace)
    - An HTTP URL: "https://..."                    (fal.ai, future providers)
    Returns (image_bytes, mime_type).
    """
    if result.startswith("data:"):
        header, b64 = result.split(",", 1)
        mime = header.split(";")[0].replace("data:", "")
        return base64.b64decode(b64), mime
    # HTTP URL — download synchronously via httpx
    with httpx.Client(timeout=60.0) as client:
        resp = client.get(result)
        resp.raise_for_status()
        mime = resp.headers.get("content-type", "image/jpeg").split(";")[0]
        return resp.content, mime


class RenderService:
    def __init__(
        self,
        render_provider: BaseRenderProvider,
        storage_service: StorageService,
        db: Client,
    ) -> None:
        self._provider = render_provider
        self._storage = storage_service
        self._db = db

    def create_render_jobs(self, spec_id: str, project_id: str, user_id: str, views: list[str]) -> list[dict]:
        rows = []
        for view in views:
            row = {
                "id": str(uuid.uuid4()),
                "project_id": project_id,
                "spec_id": spec_id,
                "user_id": user_id,
                "view_type": view,
                "render_status": "queued",
            }
            result = self._db.table("renders").insert(row).execute()
            rows.append(result.data[0])
        return rows

    async def generate_render(self, render_id: str, user_id: str) -> dict:
        render = (
            self._db.table("renders")
            .select("*, garment_specs(spec_json)")
            .eq("id", render_id)
            .eq("user_id", user_id)
            .single()
            .execute()
        ).data
        if not render:
            raise NotFoundError("Render", render_id)

        spec_json = render["garment_specs"]["spec_json"]
        view_type = render["view_type"]

        self._db.table("renders").update({"render_status": "generating"}).eq("id", render_id).execute()

        try:
            prompt = render_prompt(
                "rendering/render_prompt.jinja2",
                {"spec": spec_json, "view_type": view_type},
            )

            t0 = time.perf_counter()
            render_result = await self._provider.generate_render(
                prompt=prompt,
                reference_image_url=None,
                params={"steps": 28, "guidance_scale": 3.5, "width": 768, "height": 1024},
            )

            image_bytes, mime_type = _decode_render_result(render_result)
            ext = "jpg" if "jpeg" in mime_type else mime_type.split("/")[-1]

            storage_path, public_url = self._storage.upload_artifact(
                file_bytes=image_bytes,
                artifact_type=f"renders/{view_type}",
                file_name=f"{render_id}.{ext}",
                mime_type=mime_type,
                user_id=user_id,
                project_id=render["project_id"],
            )
            generation_ms = int((time.perf_counter() - t0) * 1000)

            result = self._db.table("renders").update({
                "render_status": "complete",
                "storage_path": storage_path,
                "public_url": public_url,
                "prompt_used": prompt,
                "generation_ms": generation_ms,
            }).eq("id", render_id).execute()

        except Exception as exc:
            logger.exception("Render generation failed for %s", render_id)
            self._db.table("renders").update({
                "render_status": "error",
                "error_message": str(exc)[:500],
            }).eq("id", render_id).execute()
            raise

        return result.data[0]

    def get_render(self, render_id: str, user_id: str) -> dict:
        result = (
            self._db.table("renders")
            .select("*")
            .eq("id", render_id)
            .eq("user_id", user_id)
            .single()
            .execute()
        )
        if not result.data:
            raise NotFoundError("Render", render_id)
        return result.data
