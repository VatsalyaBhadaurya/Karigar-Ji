"""A-line and straight skirt blocks."""
from __future__ import annotations

from .geometry_utils import Point, PatternPiece, apply_seam_allowance


def draft_skirt(
    waist: float,
    hip: float,
    length: float,
    style: str = "a_line",
    seam_allowance: float = 1.5,
) -> list[PatternPiece]:
    w = waist / 4
    h = hip / 4 + 2  # ease

    if style == "straight":
        hem_w = h
    elif style == "a_line":
        flare_factor = 1.15
        hem_w = h * flare_factor
    else:
        hem_w = h * 1.3  # flared

    front_points = [
        Point(0, 0),
        Point(w, 0),
        Point(hem_w, length),
        Point(0, length),
    ]
    back_points = [
        Point(0, 0),
        Point(w, 0),
        Point(hem_w, length),
        Point(0, length),
    ]

    fx = hem_w / 2
    front = PatternPiece(
        name="skirt_front",
        points=apply_seam_allowance(front_points, seam_allowance),
        grain_line=(Point(fx, length * 0.1), Point(fx, length * 0.9)),
        labels=[(Point(fx, length * 0.45), "SKIRT\nFRONT\nCut 1\non fold")],
    )
    bx = hem_w / 2
    back = PatternPiece(
        name="skirt_back",
        points=apply_seam_allowance(back_points, seam_allowance),
        grain_line=(Point(bx, length * 0.1), Point(bx, length * 0.9)),
        labels=[(Point(bx, length * 0.45), "SKIRT\nBACK\nCut 1\non fold")],
    )
    return [front, back]
