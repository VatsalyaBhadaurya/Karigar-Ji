from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class Measurements(BaseModel):
    chest: Optional[float] = None
    waist: Optional[float] = None
    hip: Optional[float] = None
    length: Optional[float] = None
    sleeve_length: Optional[float] = None
    shoulder_width: Optional[float] = None
    unit: str = "cm"


class CollarSpec(BaseModel):
    type: Optional[str] = None
    height: Optional[float] = None
    notes: Optional[str] = None


class CuffSpec(BaseModel):
    type: Optional[str] = None
    width: Optional[float] = None
    closure: Optional[str] = None


class ClosureSpec(BaseModel):
    type: Optional[str] = None
    placement: Optional[str] = None
    hardware: Optional[str] = None
    length: Optional[float] = None


class PocketSpec(BaseModel):
    type: Optional[str] = None
    placement: Optional[str] = None
    dimensions: Optional[dict] = None


class EmbroiderySpec(BaseModel):
    present: bool = False
    technique: Optional[str] = None
    placement: Optional[list[str]] = None
    thread_colors: Optional[list[str]] = None


class SpecMetadata(BaseModel):
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    prompt_version: Optional[str] = None
    source_type: Optional[str] = None  # 'hand_drawn' | 'cad' | 'photo'
    notes: Optional[str] = None


class GarmentSpec(BaseModel):
    garment_type: str
    silhouette: str
    neckline: Optional[str] = None
    sleeve_type: Optional[str] = None
    fit: str
    panels: list[str] = Field(default_factory=list)
    pockets: list[PocketSpec] = Field(default_factory=list)
    collar: Optional[CollarSpec] = None
    cuff: Optional[CuffSpec] = None
    closure: Optional[ClosureSpec] = None
    trims: list[str] = Field(default_factory=list)
    embroidery: Optional[EmbroiderySpec] = None
    construction_notes: list[str] = Field(default_factory=list)
    suggested_fabric: list[str] = Field(default_factory=list)
    colors: list[str] = Field(default_factory=list)
    measurements: Optional[Measurements] = None
    seam_allowance: str = "1.5cm"
    metadata: SpecMetadata = Field(default_factory=SpecMetadata)

    model_config = {"json_schema_extra": {"example": {
        "garment_type": "anarkali_kurta",
        "silhouette": "flared",
        "neckline": "V-neck",
        "sleeve_type": "set-in",
        "fit": "fitted_bodice_flared_skirt",
        "panels": ["bodice_front", "bodice_back", "skirt_panels_x6", "sleeve_x2"],
        "pockets": [{"type": "side_seam", "placement": "hip", "dimensions": {"width": 15, "depth": 18}}],
        "trims": ["embroidered_border", "tassel_hem"],
        "embroidery": {"present": True, "technique": "zardozi", "placement": ["neckline", "hem_border"], "thread_colors": ["gold"]},
        "construction_notes": ["French seams on all curved seams"],
        "suggested_fabric": ["georgette", "chiffon"],
        "colors": ["deep_teal", "gold"],
        "measurements": {"chest": 90, "waist": 72, "hip": 96, "length": 140, "sleeve_length": 58, "shoulder_width": 38, "unit": "cm"},
        "seam_allowance": "1.5cm",
        "metadata": {"confidence": 0.92, "prompt_version": "v1.0.0", "source_type": "hand_drawn"},
    }}}


# JSON Schema for passing to Gemini as response_schema
GARMENT_SPEC_JSON_SCHEMA = GarmentSpec.model_json_schema()
