from __future__ import annotations

from dataclasses import dataclass

FABRIC_WIDTH_CM = 114.0  # standard fabric width
EASE_FACTOR = 1.15       # 15% wastage / layout inefficiency


@dataclass
class FabricEstimate:
    garment_type: str
    fabric_width_cm: float
    estimated_meters: float
    breakdown: dict[str, float]
    notes: list[str]


def estimate_fabric(spec_json: dict) -> FabricEstimate:
    """
    Pure-math fabric estimation. No AI involved.
    Based on measurements from the garment spec.
    """
    m = spec_json.get("measurements") or {}
    garment_type = spec_json.get("garment_type", "unknown").lower()
    notes: list[str] = []
    breakdown: dict[str, float] = {}

    chest = float(m.get("chest") or 90)
    waist = float(m.get("waist") or 72)
    hip = float(m.get("hip") or 96)
    length = float(m.get("length") or 100)
    sleeve_length = float(m.get("sleeve_length") or 60)
    unit = m.get("unit", "cm")

    if unit == "inch":
        chest *= 2.54
        waist *= 2.54
        hip *= 2.54
        length *= 2.54
        sleeve_length *= 2.54

    max_width = max(chest, hip) / 2 + 6  # half-width + seam/ease
    fabric_width = FABRIC_WIDTH_CM

    if "kurta" in garment_type or "dress" in garment_type or "anarkali" in garment_type:
        body_meters = (length / 100) * 2 * EASE_FACTOR
        sleeve_meters = (sleeve_length / 100) * 2 * EASE_FACTOR if "sleeveless" not in garment_type else 0
        total = body_meters + sleeve_meters
        breakdown = {"body": round(body_meters, 2), "sleeves": round(sleeve_meters, 2)}

    elif "saree" in garment_type:
        total = 6.0
        breakdown = {"saree_length": 6.0}
        notes.append("Standard saree: 6 meters")

    elif "blazer" in garment_type or "jacket" in garment_type:
        body_meters = (length / 100) * 2.5 * EASE_FACTOR
        sleeve_meters = (sleeve_length / 100) * 2 * EASE_FACTOR
        total = body_meters + sleeve_meters
        breakdown = {"body": round(body_meters, 2), "sleeves": round(sleeve_meters, 2)}

    else:
        total = (length / 100) * 2.2 * EASE_FACTOR
        breakdown = {"body": round(total, 2)}
        notes.append("Generic estimate — garment type not recognized")

    if spec_json.get("embroidery", {}).get("present"):
        notes.append("Add 10–15% extra fabric for embroidery placement requirements")

    return FabricEstimate(
        garment_type=garment_type,
        fabric_width_cm=fabric_width,
        estimated_meters=round(total, 2),
        breakdown=breakdown,
        notes=notes,
    )
