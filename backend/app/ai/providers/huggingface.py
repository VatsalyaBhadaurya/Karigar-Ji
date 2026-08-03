from __future__ import annotations

import asyncio
import base64
import logging
from typing import Any

import httpx

from app.ai.base import BaseRenderProvider
from app.ai.retry import ai_retry
from app.exceptions import AIProviderError

logger = logging.getLogger(__name__)

HF_INFERENCE_URL = "https://api-inference.huggingface.co/models/{model}"
# FLUX.1-Kontext also exposes a dedicated Inference Endpoint format:
HF_KONTEXT_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-Kontext-dev"


class HuggingFaceRenderProvider(BaseRenderProvider):
    """
    FLUX.1-Kontext-dev via HuggingFace Inference API.
    Free tier: https://huggingface.co/settings/tokens
    Rate limits apply on free tier. Model may queue — waits handled by retry.
    """

    def __init__(self, hf_token: str, model: str = "black-forest-labs/FLUX.1-Kontext-dev") -> None:
        self._token = hf_token
        self._model = model
        self._url = HF_INFERENCE_URL.format(model=model)

    @ai_retry
    async def generate_render(
        self,
        prompt: str,
        reference_image_url: str | None,
        params: dict[str, Any],
    ) -> str:
        """
        Call HuggingFace Inference API for FLUX.1-Kontext-dev.
        Returns a data URL (base64) or raises AIProviderError.

        FLUX.1-Kontext supports:
          - text-to-image: { "inputs": "prompt" }
          - image-to-image: { "inputs": "prompt", "image": "<base64>" }
        """
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
            "X-Wait-For-Model": "true",  # wait if model is loading, don't 503
        }

        payload: dict[str, Any] = {
            "inputs": prompt,
            "parameters": {
                "num_inference_steps": params.get("steps", 28),
                "guidance_scale": params.get("guidance_scale", 3.5),
                "width": params.get("width", 768),
                "height": params.get("height", 1024),
            },
        }

        # If a reference image is provided (for Kontext image-to-image editing)
        if reference_image_url:
            image_b64 = await self._fetch_image_as_base64(reference_image_url)
            if image_b64:
                payload["image"] = image_b64

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(self._url, headers=headers, json=payload)

                if response.status_code == 503:
                    # Model is loading — the retry decorator will handle it
                    estimated = response.json().get("estimated_time", "unknown")
                    raise AIProviderError("HuggingFace", f"Model loading, estimated wait: {estimated}s")

                if response.status_code == 429:
                    raise AIProviderError("HuggingFace", "Rate limit reached. Retry after cooldown.")

                if not response.is_success:
                    detail = response.text[:300]
                    raise AIProviderError("HuggingFace", f"HTTP {response.status_code}: {detail}")

                # HF Inference API returns raw image bytes for image models
                image_bytes = response.content
                if not image_bytes:
                    raise AIProviderError("HuggingFace", "Empty image response")

                # Return as data URL so the render service can store it
                b64 = base64.b64encode(image_bytes).decode()
                content_type = response.headers.get("content-type", "image/jpeg").split(";")[0]
                return f"data:{content_type};base64,{b64}"

        except AIProviderError:
            raise
        except Exception as exc:
            logger.exception("HuggingFace render failed")
            raise AIProviderError("HuggingFace", str(exc)) from exc

    async def _fetch_image_as_base64(self, image_url: str) -> str | None:
        """Download an image URL and return as base64 string."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(image_url)
                if resp.is_success:
                    return base64.b64encode(resp.content).decode()
        except Exception:
            logger.warning("Could not fetch reference image: %s", image_url)
        return None
