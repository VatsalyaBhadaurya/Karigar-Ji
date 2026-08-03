"""
Standard metric bodice block draft.
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

    c = (chest + ease["chest"]) / 4   # quarter chest with ease
    w = (waist + ease["waist"]) / 4   # quarter waist with ease
    sh = shoulder_width / 2            # half shoulder width

    # Key construction measurements
    nk_w = c * 0.28            # neck width (approx 1/6 chest circ)
    nk_f = nk_w * 0.6          # front neck depth
    nk_b = nk_w * 0.25         # back neck depth (shallower)
    sh_slope = 1.5              # shoulder slope (cm drop from neck to shoulder tip)
    arm_depth = chest / 6 + 2  # armhole depth from shoulder

    # Waist shaping: ease in slightly at waist, then back out (ignored for simplicity — we taper)
    waist_dart = (c - w) * 0.6  # amount of waist shaping on this panel

    # ── FRONT BODICE ──────────────────────────────────────────
    # Points clockwise from CF neckline
    cf_neck  = Point(0, nk_f)                          # CF neckline (below center)
    sh_neck  = Point(nk_w, 0)                          # Shoulder/neck intersection
    sh_tip   = Point(sh, sh_slope)                     # Shoulder tip
    # Armhole: 3-point approximation of armhole curve
    arm1     = Point(sh + (c - sh) * 0.55, arm_depth * 0.35)  # upper armhole
    arm2     = Point(c, arm_depth * 0.65)                       # mid armhole
    underarm = Point(c, arm_depth)                              # underarm point
    # Side seam tapering to waist then straight to hem
    waist_s  = Point(c - waist_dart * 0.5, back_length)        # waist at side seam
    cf_waist = Point(0, back_length)                            # CF waist

    front_pts = [cf_neck, sh_neck, sh_tip, arm1, arm2, underarm, waist_s, cf_waist]
    cx = c * 0.5
    cy = arm_depth + (back_length - arm_depth) * 0.5

    front = PatternPiece(
        name="bodice_front",
        points=apply_seam_allowance(front_pts, seam_allowance),
        grain_line=(Point(cx, arm_depth + (back_length - arm_depth) * 0.15),
                    Point(cx, arm_depth + (back_length - arm_depth) * 0.85)),
        labels=[(Point(cx, cy), "BODICE FRONT\nCut 1 on fold")],
    )

    # ── BACK BODICE ───────────────────────────────────────────
    cb_neck  = Point(0, nk_b)
    bsh_neck = Point(nk_w, 0)
    bsh_tip  = Point(sh, sh_slope + 0.5)
    barm1    = Point(sh + (c - sh) * 0.55, arm_depth * 0.35)
    barm2    = Point(c, arm_depth * 0.65)
    bunderarm = Point(c, arm_depth)
    bwaist_s = Point(c - waist_dart * 0.5, back_length)
    cb_waist = Point(0, back_length)

    back_pts = [cb_neck, bsh_neck, bsh_tip, barm1, barm2, bunderarm, bwaist_s, cb_waist]

    back = PatternPiece(
        name="bodice_back",
        points=apply_seam_allowance(back_pts, seam_allowance),
        grain_line=(Point(cx, arm_depth + (back_length - arm_depth) * 0.15),
                    Point(cx, arm_depth + (back_length - arm_depth) * 0.85)),
        labels=[(Point(cx, cy), "BODICE BACK\nCut 1 on fold")],
    )

    return [front, back]
