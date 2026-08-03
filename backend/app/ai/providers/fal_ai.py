from __future__ import annotations

import logging
from typing import Any

import fal_client

from app.ai.base import BaseRenderProvider
from app.ai.retry import ai_retry
from app.exceptions import AIProviderError

logger = logging.getLogger(__name__)


class FalAiProvider(BaseRenderProvider):
    def __init__(self, api_key: str, model: str = "fal-ai/flux-kontext/dev") -> None:
        import os
        os.environ["FAL_KEY"] = api_key
        self._model = model

    @ai_retry
    async def generate_render(
        self,
        prompt: str,
        reference_image_url: str | None,
        params: dict[str, Any],
    ) -> str:
        """Submit render job and return public URL of generated image."""
        try:
            arguments: dict[str, Any] = {
                "prompt": prompt,
                "num_inference_steps": params.get("steps", 28),
                "guidance_scale": params.get("guidance_scale", 3.5),
                "num_images": 1,
                "enable_safety_checker": False,
                **{k: v for k, v in params.items() if k not in ("steps", "guidance_scale")},
            }
            if reference_image_url:
                arguments["image_url"] = reference_image_url

            result = await fal_client.run_async(self._model, arguments=arguments)

            images = result.get("images") or []
            if not images:
                raise AIProviderError("fal.ai", "No images returned")

            return images[0]["url"]
        except AIProviderError:
            raise
        except Exception as exc:
            logger.exception("fal.ai generate_render failed")
            raise AIProviderError("fal.ai", str(exc)) from exc
