from __future__ import annotations

import logging
import uuid

from supabase import Client

from app.ai.base import BaseRenderProvider
from app.ai.prompt_loader import render_prompt
from app.exceptions import NotFoundError
from app.services.storage_service import StorageService

logger = logging.getLogger(__name__)

VIEW_TYPES = ["front", "back", "side_left", "studio_3q"]


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
        """Create queued render rows for each requested view."""
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
        """Generate a single render. Called per view after job creation."""
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

        prompt = render_prompt(
            "rendering/render_prompt.jinja2",
            {"spec": spec_json, "view_type": view_type},
        )

        import httpx, time
        start = time.perf_counter()
        image_url = await self._provider.generate_render(
            prompt=prompt,
            reference_image_url=None,
            params={"steps": 28, "guidance_scale": 3.5},
        )

        # Download and re-upload to Supabase Storage for permanent storage
        async with httpx.AsyncClient() as client:
            resp = await client.get(image_url, timeout=60)
            resp.raise_for_status()
            image_bytes = resp.content

        storage_path, public_url = self._storage.upload_artifact(
            file_bytes=image_bytes,
            artifact_type=f"renders/{view_type}",
            file_name=f"{render_id}.webp",
            mime_type="image/webp",
            user_id=user_id,
            project_id=render["project_id"],
        )
        generation_ms = int((time.perf_counter() - start) * 1000)

        result = self._db.table("renders").update({
            "render_status": "complete",
            "storage_path": storage_path,
            "public_url": public_url,
            "prompt_used": prompt,
            "generation_ms": generation_ms,
        }).eq("id", render_id).execute()

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
