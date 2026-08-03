from __future__ import annotations

import logging
from typing import Any

import httpx

from app.ai.base import BaseRenderProvider
from app.ai.retry import ai_retry
from app.exceptions import AIProviderError

logger = logging.getLogger(__name__)

# HF router → together provider (OpenAI-compatible images API)
HF_TOGETHER_URL = "https://router.huggingface.co/together/v1/images/generations"


class HuggingFaceRenderProvider(BaseRenderProvider):
    """
    Text-to-image via HuggingFace router → Together AI provider.
    Uses OpenAI-compatible images/generations endpoint.
    Supported models: black-forest-labs/FLUX.1-schnell
    """

    def __init__(self, hf_token: str, model: str = "black-forest-labs/FLUX.1-schnell") -> None:
        self._token = hf_token
        self._model = model

    @ai_retry
    async def generate_render(
        self,
        prompt: str,
        reference_image_url: str | None,
        params: dict[str, Any],
    ) -> str:
        """
        Generate an image via HF router → together.
        Returns a public URL (together hosts it for ~1 hour).
        reference_image_url is accepted but ignored — FLUX.1-schnell is text-to-image only.
        """
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }

        payload: dict[str, Any] = {
            "model": self._model,
            "prompt": prompt,
            "n": 1,
            "width": params.get("width", 768),
            "height": params.get("height", 1024),
        }

        steps = params.get("steps")
        if steps:
            payload["num_inference_steps"] = steps

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(HF_TOGETHER_URL, headers=headers, json=payload)

                if response.status_code == 429:
                    raise AIProviderError("HuggingFace", "Rate limit reached. Retry after cooldown.")

                if not response.is_success:
                    detail = response.text[:300]
                    raise AIProviderError("HuggingFace", f"HTTP {response.status_code}: {detail}")

                data = response.json()
                items = data.get("data", [])
                if not items:
                    raise AIProviderError("HuggingFace", "Empty response — no image data returned")

                # together returns a URL; render_service._decode_render_result handles both URLs and data URLs
                url = items[0].get("url") or items[0].get("b64_json")
                if not url:
                    raise AIProviderError("HuggingFace", f"No url/b64_json in response: {data}")

                return url

        except AIProviderError:
            raise
        except Exception as exc:
            logger.exception("HuggingFace render failed")
            raise AIProviderError("HuggingFace", str(exc)) from exc
