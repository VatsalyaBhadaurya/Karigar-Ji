"""
Deterministic pattern engine — generates SVG cutting patterns from GarmentSpec.
No AI involved: pure geometry.
"""
from __future__ import annotations

import sys
import uuid
import logging
from pathlib import Path

from supabase import Client

from app.exceptions import NotFoundError
from app.services.storage_service import StorageService

# Resolve ai/pattern_engine on sys.path
_AI_DIR = Path(__file__).resolve().parents[3] / "ai"
if str(_AI_DIR) not in sys.path:
    sys.path.insert(0, str(_AI_DIR))

from pattern_engine.geometry_utils import PatternPiece, Point  # noqa: E402
from pattern_engine.bodice_block import draft_bodice  # noqa: E402
from pattern_engine.skirt_block import draft_skirt  # noqa: E402
from pattern_engine.sleeve_block import draft_sleeve  # noqa: E402

logger = logging.getLogger(__name__)

# Default measurements (cm) when spec has none / zeroes
_DEFAULTS = {
    "chest": 90.0, "waist": 72.0, "hip": 96.0,
    "length": 60.0, "sleeve_length": 58.0, "shoulder_width": 38.0,
}

_SCALE = 2.5  # pixels per cm in SVG


def _cm(value: float | None, key: str) -> float:
    """Use value if meaningful, otherwise default."""
    return value if (value and value > 0) else _DEFAULTS[key]


def _piece_to_svg_path(piece: PatternPiece, offset_x: float = 0, offset_y: float = 0) -> str:
    pts = piece.points
    if not pts:
        return ""
    scale = _SCALE
    d = f"M {pts[0].x * scale + offset_x:.1f},{pts[0].y * scale + offset_y:.1f}"
    for p in pts[1:]:
        d += f" L {p.x * scale + offset_x:.1f},{p.y * scale + offset_y:.1f}"
    d += " Z"
    return d


def _render_svg(pieces: list[PatternPiece]) -> bytes:
    scale = _SCALE
    margin = 20

    # Compute canvas size from all points
    all_x = [p.x * scale for piece in pieces for p in piece.points]
    all_y = [p.y * scale for piece in pieces for p in piece.points]
    if not all_x:
        return b"<svg></svg>"

    # Lay out pieces side by side with gaps
    svg_parts = []
    x_cursor = margin

    for piece in pieces:
        if not piece.points:
            continue
        piece_w = (max(p.x for p in piece.points) - min(p.x for p in piece.points)) * scale
        piece_h = (max(p.y for p in piece.points) - min(p.y for p in piece.points)) * scale
        min_px = min(p.x for p in piece.points) * scale
        min_py = min(p.y for p in piece.points) * scale
        ox = x_cursor - min_px
        oy = margin - min_py

        path_d = _piece_to_svg_path(piece, ox, oy)
        svg_parts.append(f'<path d="{path_d}" fill="#1e293b" stroke="#94a3b8" stroke-width="1.5"/>')

        # Grain line
        if piece.grain_line:
            g1, g2 = piece.grain_line
            svg_parts.append(
                f'<line x1="{g1.x*scale+ox:.1f}" y1="{g1.y*scale+oy:.1f}" '
                f'x2="{g2.x*scale+ox:.1f}" y2="{g2.y*scale+oy:.1f}" '
                f'stroke="#60a5fa" stroke-width="1" stroke-dasharray="4,3" marker-end="url(#arrow)"/>'
            )

        # Label
        for lp, text in (piece.labels or []):
            lx, ly = lp.x * scale + ox, lp.y * scale + oy
            for i, line in enumerate(text.split("\n")):
                svg_parts.append(
                    f'<text x="{lx:.1f}" y="{ly + i*14:.1f}" '
                    f'fill="#e2e8f0" font-size="10" text-anchor="middle" '
                    f'font-family="monospace">{line}</text>'
                )

        x_cursor += piece_w + 30

    total_w = x_cursor + margin
    total_h = max((max(p.y for p in piece.points) - min(p.y for p in piece.points)) * scale for piece in pieces if piece.points) + margin * 2

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{total_w:.0f}" height="{total_h:.0f}" viewBox="0 0 {total_w:.0f} {total_h:.0f}">
  <defs>
    <marker id="arrow" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto">
      <path d="M0,0 L0,6 L6,3 z" fill="#60a5fa"/>
    </marker>
  </defs>
  <rect width="100%" height="100%" fill="#0f172a"/>
  {''.join(svg_parts)}
</svg>"""
    return svg.encode()


class PatternEngineService:
    def __init__(self, storage: StorageService, db: Client) -> None:
        self._storage = storage
        self._db = db

    def generate(self, spec_id: str, project_id: str, user_id: str, sizes: list[str]) -> dict:
        spec_row = (
            self._db.table("garment_specs")
            .select("spec_json")
            .eq("id", spec_id)
            .eq("user_id", user_id)
            .single()
            .execute()
        )
        if not spec_row.data:
            raise NotFoundError("GarmentSpec", spec_id)

        spec = spec_row.data["spec_json"]
        m = spec.get("measurements") or {}
        seam_str = spec.get("seam_allowance", "1.5cm")
        try:
            seam = float("".join(c for c in seam_str if c.isdigit() or c == "."))
        except ValueError:
            seam = 1.5

        chest = _cm(m.get("chest"), "chest")
        waist = _cm(m.get("waist"), "waist")
        hip = _cm(m.get("hip"), "hip")
        length = _cm(m.get("length"), "length")
        sleeve_length = _cm(m.get("sleeve_length"), "sleeve_length")
        shoulder_width = _cm(m.get("shoulder_width"), "shoulder_width")

        garment = spec.get("garment_type", "").lower()
        silhouette = spec.get("silhouette", "").lower()

        pieces: list[PatternPiece] = []

        if any(k in garment for k in ["lehenga", "skirt"]):
            style = "flared" if "flared" in silhouette else "a_line"
            pieces += draft_skirt(waist, hip, length, style, seam)
        elif any(k in garment for k in ["kurta", "shirt", "top", "blouse", "choli"]):
            pieces += draft_bodice(chest, waist, length, shoulder_width, seam)
        else:
            # Generic: bodice + skirt if long, bodice only if short
            pieces += draft_bodice(chest, waist, min(length, 70), shoulder_width, seam)
            if length > 70:
                pieces += draft_skirt(waist, hip, length - 30, silhouette or "a_line", seam)

        sleeve_type = spec.get("sleeve_type", "")
        if sleeve_type and "sleeveless" not in sleeve_type and "none" not in sleeve_type:
            pieces.append(draft_sleeve(sleeve_length, chest / 3, seam))

        svg_bytes = _render_svg(pieces)
        row_id = str(uuid.uuid4())
        storage_path, public_url = self._storage.upload_artifact(
            file_bytes=svg_bytes,
            artifact_type="patterns",
            file_name=f"{row_id}.svg",
            mime_type="image/svg+xml",
            user_id=user_id,
            project_id=project_id,
        )

        # Upsert pattern row
        existing = (
            self._db.table("patterns")
            .select("id")
            .eq("project_id", project_id)
            .eq("spec_id", spec_id)
            .limit(1)
            .execute()
        )
        piece_names = [p.name for p in pieces]
        if existing.data:
            self._db.table("patterns").update({
                "svg_storage_path": storage_path,
                "geometry_params": {"pieces": piece_names, "svg_url": public_url},
                "pattern_status": "complete",
            }).eq("id", existing.data[0]["id"]).execute()
            pattern_id = existing.data[0]["id"]
        else:
            self._db.table("patterns").insert({
                "id": row_id,
                "project_id": project_id,
                "spec_id": spec_id,
                "user_id": user_id,
                "piece_name": piece_names[0] if piece_names else "full_pattern",
                "svg_storage_path": storage_path,
                "geometry_params": {"pieces": piece_names, "svg_url": public_url},
                "pattern_status": "complete",
            }).execute()
            pattern_id = row_id

        return {
            "id": pattern_id,
            "svg_url": public_url,
            "pieces": piece_names,
            "piece_count": len(pieces),
        }
