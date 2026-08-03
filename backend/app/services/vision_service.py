from __future__ import annotations

import logging
import uuid
from datetime import datetime

from supabase import Client

from app.ai.base import BaseVisionProvider
from app.ai.prompt_loader import render_prompt
from app.exceptions import NotFoundError, AIProviderError
from app.schemas.garment_spec import GarmentSpec, GARMENT_SPEC_JSON_SCHEMA

logger = logging.getLogger(__name__)

PROMPT_VERSION = "v1.0.0"


class VisionService:
    def __init__(self, vision_provider: BaseVisionProvider, db: Client) -> None:
        self._provider = vision_provider
        self._db = db

    async def analyze_sketch(
        self,
        upload_id: str,
        project_id: str,
        user_id: str,
        user_notes: str = "",
    ) -> dict:
        # Load upload record
        result = (
            self._db.table("uploads")
            .select("public_url, file_name")
            .eq("id", upload_id)
            .eq("user_id", user_id)
            .single()
            .execute()
        )
        if not result.data:
            raise NotFoundError("Upload", upload_id)

        image_url: str = result.data["public_url"]

        prompt = render_prompt(
            "vision/garment_analysis.jinja2",
            {
                "source_type": "hand_drawn",
                "user_notes": user_notes or "None provided",
                "target_market": "Indian fashion market",
                "spec_version": PROMPT_VERSION,
            },
        )

        raw_response = await self._provider.analyze_garment(
            image_url=image_url,
            prompt=prompt,
            response_schema=GARMENT_SPEC_JSON_SCHEMA,
        )

        spec = GarmentSpec.model_validate(raw_response)
        spec.metadata.prompt_version = PROMPT_VERSION
        spec.metadata.source_type = "hand_drawn"

        spec_data = {
            "id": str(uuid.uuid4()),
            "project_id": project_id,
            "upload_id": upload_id,
            "user_id": user_id,
            "version": 1,
            "is_current": True,
            "garment_type": spec.garment_type,
            "silhouette": spec.silhouette,
            "neckline": spec.neckline,
            "sleeve_type": spec.sleeve_type,
            "fit": spec.fit,
            "spec_json": spec.model_dump(mode="json"),
            "ai_confidence": spec.metadata.confidence,
            "ai_provider": "gemini-2.5-flash",
            "prompt_version": PROMPT_VERSION,
            "raw_ai_response": raw_response,
        }

        # Set any existing specs as non-current
        self._db.table("garment_specs").update({"is_current": False}).eq(
            "project_id", project_id
        ).eq("is_current", True).execute()

        insert_result = self._db.table("garment_specs").insert(spec_data).execute()

        # Update project status
        self._db.table("projects").update(
            {"status": "spec_ready", "garment_type": spec.garment_type}
        ).eq("id", project_id).execute()

        return insert_result.data[0]

    def get_spec(self, spec_id: str, user_id: str) -> dict:
        result = (
            self._db.table("garment_specs")
            .select("*")
            .eq("id", spec_id)
            .eq("user_id", user_id)
            .single()
            .execute()
        )
        if not result.data:
            raise NotFoundError("GarmentSpec", spec_id)
        return result.data

    def update_spec(self, spec_id: str, user_id: str, updates: dict) -> dict:
        # Re-validate the spec_json if provided
        if "spec_json" in updates:
            validated = GarmentSpec.model_validate(updates["spec_json"])
            updates["spec_json"] = validated.model_dump(mode="json")
            updates.update({
                "garment_type": validated.garment_type,
                "silhouette": validated.silhouette,
                "neckline": validated.neckline,
                "sleeve_type": validated.sleeve_type,
                "fit": validated.fit,
            })

        result = (
            self._db.table("garment_specs")
            .update(updates)
            .eq("id", spec_id)
            .eq("user_id", user_id)
            .execute()
        )
        if not result.data:
            raise NotFoundError("GarmentSpec", spec_id)
        return result.data[0]
