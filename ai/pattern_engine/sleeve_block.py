"""Standard set-in sleeve block with parabolic cap curve."""
from __future__ import annotations

from .geometry_utils import Point, PatternPiece, apply_seam_allowance


def draft_sleeve(
    sleeve_length: float,
    upper_arm: float = 30.0,
    seam_allowance: float = 1.5,
) -> PatternPiece:
    ua = upper_arm + 4              # upper arm + ease
    half_w = ua / 2                 # half-width (piece is full width, cut 2)
    full_w = ua                     # total sleeve width
    cap_h = ua * 0.3               # sleeve cap height
    cuff_w = ua * 0.82              # cuff slightly narrower than cap
    cuff_inset = (full_w - cuff_w) / 2  # taper amount per side

    # Sleeve cap — 9-point parabolic approximation
    # from left underarm (0, cap_h) up to crown (half_w, 0) and back down to right underarm (full_w, cap_h)
    cap_pts: list[Point] = []
    n = 10
    for i in range(n + 1):
        t = i / n
        x = t * full_w
        rise = cap_h * 4 * t * (1 - t)   # parabola: max at center, 0 at edges
        cap_pts.append(Point(x, cap_h - rise))

    # Full outline: left cuff → left underarm → cap curve → right underarm → right cuff
    left_cuff   = Point(cuff_inset, cap_h + sleeve_length)
    right_cuff  = Point(full_w - cuff_inset, cap_h + sleeve_length)
    # cap_pts[0] = left underarm (0, cap_h), cap_pts[-1] = right underarm (full_w, cap_h)

    all_pts = [left_cuff] + cap_pts + [right_cuff]

    cx = half_w
    cy = cap_h + sleeve_length * 0.5

    return PatternPiece(
        name="sleeve",
        points=apply_seam_allowance(all_pts, seam_allowance),
        grain_line=(Point(cx, cap_h + sleeve_length * 0.2),
                    Point(cx, cap_h + sleeve_length * 0.8)),
        labels=[(Point(cx, cy), "SLEEVE\nCut 2")],
    )
