from __future__ import annotations

import io
import logging
import uuid
import zipfile

from supabase import Client

from app.exceptions import NotFoundError
from app.services.storage_service import StorageService

logger = logging.getLogger(__name__)


class ExportService:
    def __init__(self, storage_service: StorageService, db: Client) -> None:
        self._storage = storage_service
        self._db = db

    async def create_export(
        self,
        project_id: str,
        user_id: str,
        export_type: str,
        include: list[str],
    ) -> dict:
        row_id = str(uuid.uuid4())
        self._db.table("exports").insert({
            "id": row_id, "project_id": project_id, "user_id": user_id,
            "export_type": export_type, "includes": include, "export_status": "generating",
        }).execute()

        if export_type == "zip":
            zip_bytes = await self._bundle_zip(project_id, user_id, include)
            storage_path, public_url = self._storage.upload_artifact(
                file_bytes=zip_bytes,
                artifact_type="exports",
                file_name=f"{row_id}.zip",
                mime_type="application/zip",
                user_id=user_id,
                project_id=project_id,
            )
            signed_url = self._storage.create_signed_url(storage_path, expires_in=86400)
        else:
            signed_url = public_url = ""
            storage_path = ""

        result = self._db.table("exports").update({
            "storage_path": storage_path,
            "public_url": public_url,
            "export_status": "complete",
        }).eq("id", row_id).execute()

        row = result.data[0]
        row["signed_url"] = signed_url
        return row

    async def _bundle_zip(self, project_id: str, user_id: str, include: list[str]) -> bytes:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            if "renders" in include:
                renders = (
                    self._db.table("renders")
                    .select("view_type, storage_path, public_url")
                    .eq("project_id", project_id)
                    .eq("render_status", "complete")
                    .execute()
                ).data or []
                for r in renders:
                    if r.get("public_url"):
                        import httpx
                        async with httpx.AsyncClient() as client:
                            resp = await client.get(r["public_url"], timeout=30)
                            if resp.is_success:
                                zf.writestr(f"renders/{r['view_type']}.webp", resp.content)

            if "techpack" in include:
                tp = (
                    self._db.table("techpacks")
                    .select("pdf_url")
                    .eq("project_id", project_id)
                    .eq("pack_status", "complete")
                    .limit(1)
                    .execute()
                ).data
                if tp and tp[0].get("pdf_url"):
                    import httpx
                    async with httpx.AsyncClient() as client:
                        resp = await client.get(tp[0]["pdf_url"], timeout=30)
                        if resp.is_success:
                            zf.writestr("techpack/techpack.pdf", resp.content)

        return buf.getvalue()
