from __future__ import annotations

import json
import logging
from typing import Any

import google.generativeai as genai

from app.ai.base import BaseVisionProvider, BaseTextProvider
from app.ai.retry import ai_retry
from app.exceptions import AIProviderError

logger = logging.getLogger(__name__)


class GeminiProvider(BaseVisionProvider, BaseTextProvider):
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash") -> None:
        genai.configure(api_key=api_key)
        self._model_name = model

    def _model(self) -> genai.GenerativeModel:
        return genai.GenerativeModel(self._model_name)

    @ai_retry
    async def analyze_garment(
        self,
        image_url: str,
        prompt: str,
        response_schema: dict[str, Any],
    ) -> dict[str, Any]:
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                resp = await client.get(image_url, timeout=30)
                resp.raise_for_status()
                image_bytes = resp.content
                mime_type = resp.headers.get("content-type", "image/jpeg").split(";")[0]

            model = self._model()
            response = model.generate_content(
                contents=[
                    {"mime_type": mime_type, "data": image_bytes},
                    prompt,
                ],
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=response_schema,
                    temperature=0.1,
                ),
            )
            return json.loads(response.text)
        except Exception as exc:
            logger.exception("Gemini analyze_garment failed")
            raise AIProviderError("Gemini", str(exc)) from exc

    @ai_retry
    async def generate_structured(
        self,
        prompt: str,
        response_schema: dict[str, Any],
    ) -> dict[str, Any]:
        try:
            model = self._model()
            response = model.generate_content(
                contents=prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=response_schema,
                    temperature=0.2,
                ),
            )
            return json.loads(response.text)
        except Exception as exc:
            logger.exception("Gemini generate_structured failed")
            raise AIProviderError("Gemini", str(exc)) from exc
