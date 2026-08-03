from __future__ import annotations

import copy
import json
import logging
from typing import Any

from google import genai
from google.genai import types

from app.ai.base import BaseVisionProvider, BaseTextProvider
from app.ai.retry import ai_retry
from app.exceptions import AIProviderError

logger = logging.getLogger(__name__)

_UNSUPPORTED_KEYS = {"additionalProperties", "title", "$schema"}


def _clean_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """
    Prepare a Pydantic-generated JSON Schema for Gemini Developer API:
    - Resolve $ref/$defs (inline nested model definitions)
    - Unwrap Optional[X] = anyOf[X, null] → just X (Gemini rejects anyOf)
    - Strip unsupported keys: additionalProperties, title, $schema
    """
    schema = copy.deepcopy(schema)
    defs = schema.pop("$defs", {})

    def _resolve(node: Any) -> Any:
        if isinstance(node, dict):
            if "$ref" in node:
                ref_name = node["$ref"].split("/")[-1]
                return _resolve(defs.get(ref_name, {}))
            # Unwrap Optional[X]: anyOf with exactly one non-null branch
            if "anyOf" in node:
                non_null = [s for s in node["anyOf"] if s != {"type": "null"}]
                if len(non_null) == 1:
                    resolved = _resolve(non_null[0])
                    extras = {k: _resolve(v) for k, v in node.items()
                              if k not in _UNSUPPORTED_KEYS and k != "anyOf"}
                    return {**resolved, **extras}
            return {k: _resolve(v) for k, v in node.items() if k not in _UNSUPPORTED_KEYS}
        if isinstance(node, list):
            return [_resolve(i) for i in node]
        return node

    return _resolve(schema)


class GeminiProvider(BaseVisionProvider, BaseTextProvider):
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash") -> None:
        self._client = genai.Client(api_key=api_key)
        self._model_name = model

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

            response = await self._client.aio.models.generate_content(
                model=self._model_name,
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                    prompt,
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=_clean_schema(response_schema),
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
            response = await self._client.aio.models.generate_content(
                model=self._model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=_clean_schema(response_schema),
                    temperature=0.2,
                ),
            )
            return json.loads(response.text)
        except Exception as exc:
            logger.exception("Gemini generate_structured failed")
            raise AIProviderError("Gemini", str(exc)) from exc
