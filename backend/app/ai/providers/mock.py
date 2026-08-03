from __future__ import annotations

import asyncio
from typing import Any

from app.ai.base import BaseVisionProvider, BaseTextProvider


class MockVisionProvider(BaseVisionProvider):
    """
    Returns a hardcoded GarmentSpec for local dev when Gemini quota is unavailable.
    Swap out by pointing get_vision_provider() at GeminiProvider.
    """

    async def analyze_garment(
        self,
        image_url: str,
        prompt: str,
        response_schema: dict[str, Any],
    ) -> dict[str, Any]:
        await asyncio.sleep(1.5)  # simulate latency
        return {
            "garment_type": "anarkali_kurta",
            "silhouette": "flared",
            "neckline": "V-neck",
            "sleeve_type": "set-in",
            "fit": "fitted_bodice_flared_skirt",
            "panels": ["bodice_front", "bodice_back", "skirt_panel_x6", "sleeve_x2"],
            "pockets": [{"type": "side_seam", "placement": "hip", "dimensions": {"width": 15, "depth": 18}}],
            "collar": None,
            "cuff": {"type": "round", "width": 3.0, "closure": "button"},
            "closure": {"type": "zip", "placement": "center_back", "hardware": "concealed", "length": 35.0},
            "trims": ["embroidered_border", "tassel_hem"],
            "embroidery": {
                "present": True,
                "technique": "zardozi",
                "placement": ["neckline", "hem_border"],
                "thread_colors": ["gold", "copper"],
            },
            "construction_notes": [
                "French seams on all curved seams",
                "Interface bodice front and back",
                "Underlining recommended for skirt panels",
            ],
            "suggested_fabric": ["georgette", "chiffon", "crepe"],
            "colors": ["deep_teal", "gold"],
            "measurements": {
                "chest": 90.0,
                "waist": 72.0,
                "hip": 96.0,
                "length": 140.0,
                "sleeve_length": 58.0,
                "shoulder_width": 38.0,
                "unit": "cm",
            },
            "seam_allowance": "1.5cm",
            "metadata": {
                "confidence": 0.0,
                "prompt_version": "mock",
                "source_type": "hand_drawn",
                "notes": "MOCK RESPONSE — replace with real Gemini API key",
            },
        }


class MockTextProvider(BaseTextProvider):
    async def generate_structured(
        self,
        prompt: str,
        response_schema: dict[str, Any],
    ) -> dict[str, Any]:
        await asyncio.sleep(1.0)
        return {"mock": True, "note": "MockTextProvider — replace with real Gemini key"}
