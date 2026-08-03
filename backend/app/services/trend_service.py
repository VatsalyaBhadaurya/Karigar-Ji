from __future__ import annotations

import logging
import uuid

from supabase import Client

from app.ai.base import BaseTextProvider
from app.ai.prompt_loader import render_prompt
from app.exceptions import NotFoundError

logger = logging.getLogger(__name__)

TREND_SCHEMA = {
    "type": "object",
    "properties": {
        "trend_score": {"type": "number"},
        "novelty_score": {"type": "number"},
        "market_positioning": {"type": "string"},
        "similar_styles_seen": {"type": "array", "items": {"type": "string"}},
        "seasonal_relevance": {"type": "string"},
        "target_demographic": {"type": "string"},
        "price_range_suggestion": {
            "type": "object",
            "properties": {
                "currency": {"type": "string"},
                "min": {"type": "number"},
                "max": {"type": "number"},
            },
        },
        "sustainability_notes": {"type": "array", "items": {"type": "string"}},
        "suggestions": {"type": "array", "items": {"type": "string"}},
        "reasoning": {"type": "string"},
    },
    "required": ["trend_score", "novelty_score", "market_positioning", "suggestions"],
}


class TrendService:
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
        self._db.table("trend_reports").insert({
            "id": row_id, "project_id": project_id, "spec_id": spec_id,
            "user_id": user_id, "report_status": "generating",
        }).execute()

        prompt = render_prompt("trend/trend_analysis.jinja2", {"spec": spec_row.data["spec_json"]})
        report_json = await self._provider.generate_structured(prompt, TREND_SCHEMA)

        result = self._db.table("trend_reports").update({
            "report_json": report_json,
            "report_status": "complete",
        }).eq("id", row_id).execute()

        return result.data[0]
