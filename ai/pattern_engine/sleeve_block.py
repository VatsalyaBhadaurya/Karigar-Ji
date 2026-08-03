"""Standard set-in sleeve block."""
from __future__ import annotations

from .geometry_utils import Point, PatternPiece, apply_seam_allowance


def draft_sleeve(
    sleeve_length: float,
    upper_arm: float = 30.0,
    seam_allowance: float = 1.5,
) -> PatternPiece:
    w = upper_arm / 2 + 3  # half-sleeve width with ease
    cap_height = upper_arm * 0.35

    A = Point(0, cap_height)    # Sleeve head left
    B = Point(w, cap_height)    # Sleeve head right
    C = Point(w, cap_height + sleeve_length)  # Cuff right
    D = Point(0, cap_height + sleeve_length)  # Cuff left
    top = Point(w / 2, 0)       # Sleeve crown

    points = [top, B, C, D, A]
    return PatternPiece(
        name="sleeve",
        points=apply_seam_allowance(points, seam_allowance),
        grain_line=(Point(w / 2, cap_height + sleeve_length * 0.1), Point(w / 2, cap_height + sleeve_length * 0.9)),
        labels=[(Point(w / 2, cap_height + sleeve_length / 2), "SLEEVE\nCut 2")],
    )
