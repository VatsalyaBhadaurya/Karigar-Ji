from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined


# The ai/ directory sits two levels above this file: backend/app/ai/ → ../../ai/
AI_PROMPTS_DIR = Path(__file__).resolve().parents[3] / "ai"


@lru_cache(maxsize=1)
def _get_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(AI_PROMPTS_DIR)),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render_prompt(template_path: str, context: dict[str, Any]) -> str:
    """
    Load and render a Jinja2 prompt template.

    Args:
        template_path: Relative path from the ai/ directory, e.g. "vision/garment_analysis.jinja2"
        context: Variables to inject into the template.
    """
    env = _get_env()
    template = env.get_template(template_path)
    return template.render(**context)
