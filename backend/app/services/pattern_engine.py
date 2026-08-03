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

_SCALE = 4.0  # pixels per cm in SVG
_GAP = 50     # gap between pieces (px)
_MARGIN = 36  # canvas margin (px)


def _cm(value: float | None, key: str) -> float:
    return value if (value and value > 0) else _DEFAULTS[key]


def _build_path(points: list[Point], ox: float, oy: float) -> str:
    if not points:
        return ""
    s = _SCALE
    d = f"M {points[0].x*s+ox:.1f},{points[0].y*s+oy:.1f}"
    for p in points[1:]:
        d += f" L {p.x*s+ox:.1f},{p.y*s+oy:.1f}"
    return d + " Z"


def _render_svg(pieces: list[PatternPiece]) -> bytes:
    s = _SCALE
    margin = _MARGIN

    if not any(p.points for p in pieces):
        return b"<svg></svg>"

    svg_parts: list[str] = []
    x_cursor = margin

    # Track tallest piece for canvas height
    max_piece_h = 0.0

    for piece in pieces:
        if not piece.points:
            continue

        xs = [p.x for p in piece.points]
        ys = [p.y for p in piece.points]
        min_px, max_px = min(xs), max(xs)
        min_py, max_py = min(ys), max(ys)
        piece_w = (max_px - min_px) * s
        piece_h = (max_py - min_py) * s
        max_piece_h = max(max_piece_h, piece_h)

        ox = x_cursor - min_px * s
        oy = margin - min_py * s

        # Piece fill + stroke
        path_d = _build_path(piece.points, ox, oy)
        svg_parts.append(
            f'<path d="{path_d}" fill="#1e293b" stroke="#94a3b8" stroke-width="2" '
            f'stroke-linejoin="round"/>'
        )

        # Grain line with arrows at both ends
        if piece.grain_line:
            g1, g2 = piece.grain_line
            g1x, g1y = g1.x*s+ox, g1.y*s+oy
            g2x, g2y = g2.x*s+ox, g2.y*s+oy
            svg_parts.append(
                f'<line x1="{g1x:.1f}" y1="{g1y:.1f}" x2="{g2x:.1f}" y2="{g2y:.1f}" '
                f'stroke="#60a5fa" stroke-width="1.5" stroke-dasharray="5,3" '
                f'marker-start="url(#arrow-r)" marker-end="url(#arrow)"/>'
            )

        # Labels — each line rendered as a <tspan> with semi-transparent backdrop
        for lp, text in (piece.labels or []):
            lx = lp.x * s + ox
            ly = lp.y * s + oy
            lines = text.split("\n")
            line_h = 15
            block_h = len(lines) * line_h + 6
            block_w = max(len(ln) for ln in lines) * 7.5 + 12

            # Background pill
            svg_parts.append(
                f'<rect x="{lx - block_w/2:.1f}" y="{ly - line_h:.1f}" '
                f'width="{block_w:.1f}" height="{block_h:.1f}" '
                f'rx="4" fill="#0f172a" fill-opacity="0.75"/>'
            )
            # Text lines
            for i, line in enumerate(lines):
                ty = ly + i * line_h
                weight = "bold" if i == 0 else "normal"
                svg_parts.append(
                    f'<text x="{lx:.1f}" y="{ty:.1f}" fill="#e2e8f0" '
                    f'font-size="11" font-weight="{weight}" '
                    f'text-anchor="middle" font-family="monospace">{line}</text>'
                )

        x_cursor += piece_w + _GAP

    total_w = x_cursor - _GAP + margin
    total_h = max_piece_h + margin * 2

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{total_w:.0f}" height="{total_h:.0f}" '
        f'viewBox="0 0 {total_w:.0f} {total_h:.0f}">\n'
        f'  <defs>\n'
        f'    <marker id="arrow" markerWidth="7" markerHeight="7" refX="3.5" refY="3.5" orient="auto">\n'
        f'      <path d="M0,0 L0,7 L7,3.5 z" fill="#60a5fa"/>\n'
        f'    </marker>\n'
        f'    <marker id="arrow-r" markerWidth="7" markerHeight="7" refX="3.5" refY="3.5" orient="auto-start-reverse">\n'
        f'      <path d="M0,0 L0,7 L7,3.5 z" fill="#60a5fa"/>\n'
        f'    </marker>\n'
        f'  </defs>\n'
        f'  <rect width="100%" height="100%" fill="#0f172a"/>\n'
        + "  " + "\n  ".join(svg_parts) + "\n"
        f'</svg>'
    )
    return svg.encode()
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
