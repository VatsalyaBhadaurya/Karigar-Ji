from __future__ import annotations

import logging
import uuid

from supabase import Client

from app.ai.base import BaseTextProvider
from app.ai.prompt_loader import render_prompt
from app.exceptions import NotFoundError

logger = logging.getLogger(__name__)

MANUFACTURING_SCHEMA = {
    "type": "object",
    "properties": {
        "recommended_machines": {"type": "array", "items": {"type": "string"}},
        "needle_specification": {"type": "string"},
        "thread_specification": {"type": "string"},
        "stitch_types": {"type": "array", "items": {"type": "string"}},
        "spi": {"type": "string"},
        "seam_types": {"type": "array", "items": {"type": "string"}},
        "estimated_sam": {"type": "number"},
        "cutting_instructions": {"type": "array", "items": {"type": "string"}},
        "ironing_instructions": {"type": "string"},
        "packaging_instructions": {"type": "string"},
        "quality_checklist": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["recommended_machines", "stitch_types", "quality_checklist"],
}


class ManufacturingService:
    def __init__(self, text_provider: BaseTextProvider, db: Client) -> None:
        self._provider = text_provider
        self._db = db

    async def generate(self, spec_id: str, project_id: str, user_id: str) -> dict:
        spec_row = (
            self._db.table("garment_specs")
            .select("spec_json")
            .eq("id", spec_id)
            .eq("user_id", user_id)
            .single()
            .execute()
        )
        if not spec_row.data:
            raise NotFoundError("GarmentSpec", spec_id)

        row_id = str(uuid.uuid4())
        self._db.table("manufacturing_docs").insert({
            "id": row_id, "project_id": project_id, "spec_id": spec_id,
            "user_id": user_id, "doc_status": "generating",
        }).execute()

        prompt = render_prompt("manufacturing/manufacturing_notes.jinja2", {"spec": spec_row.data["spec_json"]})
        doc_json = await self._provider.generate_structured(prompt, MANUFACTURING_SCHEMA)

        result = self._db.table("manufacturing_docs").update({
            "doc_json": doc_json,
            "doc_status": "complete",
        }).eq("id", row_id).execute()

        return result.data[0]
