from __future__ import annotations

import logging
import uuid
from io import BytesIO

from supabase import Client

from app.ai.base import BaseTextProvider
from app.ai.prompt_loader import render_prompt
from app.exceptions import NotFoundError
from app.services.storage_service import StorageService

logger = logging.getLogger(__name__)

TECHPACK_SCHEMA = {
    "type": "object",
    "properties": {
        "description": {"type": "string"},
        "construction_details": {"type": "array", "items": {"type": "string"}},
        "bom": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "item": {"type": "string"},
                    "quantity": {"type": "string"},
                    "specification": {"type": "string"},
                },
            },
        },
        "measurements_chart": {"type": "object"},
        "stitching_specs": {"type": "array", "items": {"type": "string"}},
        "care_instructions": {"type": "array", "items": {"type": "string"}},
        "compliance_notes": {"type": "array", "items": {"type": "string"}},
        "wash_care": {"type": "string"},
        "label_content": {"type": "string"},
        "packaging_notes": {"type": "string"},
        "qc_checkpoints": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["description", "bom", "stitching_specs", "care_instructions"],
}


class TechPackService:
    def __init__(
        self,
        text_provider: BaseTextProvider,
        storage_service: StorageService,
        db: Client,
    ) -> None:
        self._provider = text_provider
        self._storage = storage_service
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
        self._db.table("techpacks").insert({
            "id": row_id, "project_id": project_id, "spec_id": spec_id,
            "user_id": user_id, "pack_status": "generating",
        }).execute()

        prompt = render_prompt("techpack/techpack_generation.jinja2", {"spec": spec_row.data["spec_json"]})
        techpack_json = await self._provider.generate_structured(prompt, TECHPACK_SCHEMA)

        pdf_bytes = self._build_pdf(techpack_json)
        storage_path, pdf_url = self._storage.upload_artifact(
            file_bytes=pdf_bytes,
            artifact_type="techpacks",
            file_name=f"{row_id}.pdf",
            mime_type="application/pdf",
            user_id=user_id,
            project_id=project_id,
        )

        result = self._db.table("techpacks").update({
            "techpack_json": techpack_json,
            "pdf_storage_path": storage_path,
            "pdf_url": pdf_url,
            "pack_status": "complete",
        }).eq("id", row_id).execute()

        return result.data[0]

    def _build_pdf(self, techpack_json: dict) -> bytes:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors

        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph("TECH PACK", styles["Title"]))
        story.append(Spacer(1, 12))

        if desc := techpack_json.get("description"):
            story.append(Paragraph(desc, styles["Normal"]))
            story.append(Spacer(1, 12))

        # BOM table
        bom = techpack_json.get("bom", [])
        if bom:
            story.append(Paragraph("Bill of Materials", styles["Heading2"]))
            table_data = [["Item", "Quantity", "Specification"]] + [
                [b.get("item", ""), b.get("quantity", ""), b.get("specification", "")]
                for b in bom
            ]
            t = Table(table_data)
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            story.append(t)
            story.append(Spacer(1, 12))

        for section, label in [("stitching_specs", "Stitching Specs"), ("care_instructions", "Care Instructions"), ("qc_checkpoints", "QC Checkpoints")]:
            items = techpack_json.get(section, [])
            if items:
                story.append(Paragraph(label, styles["Heading2"]))
                for item in items:
                    story.append(Paragraph(f"• {item}", styles["Normal"]))
                story.append(Spacer(1, 8))

        doc.build(story)
        return buf.getvalue()
