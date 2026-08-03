from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseVisionProvider(ABC):
    """Analyze an image and return structured JSON matching a response schema."""

    @abstractmethod
    async def analyze_garment(
        self,
        image_url: str,
        prompt: str,
        response_schema: dict[str, Any],
    ) -> dict[str, Any]:
        ...


class BaseRenderProvider(ABC):
    """Generate a photorealistic image from a text prompt."""

    @abstractmethod
    async def generate_render(
        self,
        prompt: str,
        reference_image_url: str | None,
        params: dict[str, Any],
    ) -> str:
        """Returns the public URL of the generated image."""
        ...


class BaseTextProvider(ABC):
    """Generate structured JSON from a text prompt."""

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        response_schema: dict[str, Any],
    ) -> dict[str, Any]:
        ...
