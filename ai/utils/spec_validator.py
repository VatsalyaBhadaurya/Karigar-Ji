"""Validate a raw dict against the GarmentSpec schema."""
from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../backend"))

from app.schemas.garment_spec import GarmentSpec
from pydantic import ValidationError


def validate_spec(data: dict) -> tuple[GarmentSpec | None, list[str]]:
    try:
        spec = GarmentSpec.model_validate(data)
        return spec, []
    except ValidationError as exc:
        errors = [f"{'.'.join(str(loc) for loc in e['loc'])}: {e['msg']}" for e in exc.errors()]
        return None, errors
