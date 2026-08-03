"""
Standard metric bodice block draft (BCS/BTEC-aligned).
All inputs in cm. Returns front and back bodice PatternPieces.
"""
from __future__ import annotations

from .geometry_utils import Point, PatternPiece, apply_seam_allowance


def draft_bodice(
    chest: float,
    waist: float,
    back_length: float,
    shoulder_width: float,
    seam_allowance: float = 1.5,
    ease: dict | None = None,
) -> list[PatternPiece]:
    if ease is None:
        ease = {"chest": 6.0, "waist": 3.0}

    c = (chest + ease["chest"]) / 4  # quarter chest (one panel)
    w = (waist + ease["waist"]) / 4
    sh = shoulder_width / 2

    # --- FRONT BODICE ---
    # Origin at top-left of front panel
    A = Point(0, 0)          # Top center front
    B = Point(c, 0)          # Top side seam
    C = Point(c, back_length)  # Bottom side seam
    D = Point(0, back_length)  # Bottom center front

    front_points = [A, B, C, D]
    front = PatternPiece(
        name="bodice_front",
        points=apply_seam_allowance(front_points, seam_allowance),
        grain_line=(Point(c / 2, back_length * 0.1), Point(c / 2, back_length * 0.9)),
        labels=[(Point(c / 2, back_length / 2), "BODICE FRONT\nCut 1 on fold")],
    )

    # --- BACK BODICE ---
    E = Point(0, 0)
    F = Point(c, 0)
    G = Point(c, back_length)
    H = Point(0, back_length)

    back_points = [E, F, G, H]
    back = PatternPiece(
        name="bodice_back",
        points=apply_seam_allowance(back_points, seam_allowance),
        grain_line=(Point(c / 2, back_length * 0.1), Point(c / 2, back_length * 0.9)),
        labels=[(Point(c / 2, back_length / 2), "BODICE BACK\nCut 1 on fold")],
    )

    return [front, back]
