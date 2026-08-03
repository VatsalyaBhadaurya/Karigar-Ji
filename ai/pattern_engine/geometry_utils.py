"""Shared geometry helpers for the pattern drafting engine."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import NamedTuple


class Point(NamedTuple):
    x: float
    y: float


@dataclass
class PatternPiece:
    name: str
    points: list[Point]
    grain_line: tuple[Point, Point] | None = None
    fold_line: list[Point] | None = None
    notches: list[Point] = field(default_factory=list)
    labels: list[tuple[Point, str]] = field(default_factory=list)


def add(a: Point, b: Point) -> Point:
    return Point(a.x + b.x, a.y + b.y)


def sub(a: Point, b: Point) -> Point:
    return Point(a.x - b.x, a.y - b.y)


def midpoint(a: Point, b: Point) -> Point:
    return Point((a.x + b.x) / 2, (a.y + b.y) / 2)


def distance(a: Point, b: Point) -> float:
    return math.hypot(b.x - a.x, b.y - a.y)


def offset_point(p: Point, angle_deg: float, length: float) -> Point:
    rad = math.radians(angle_deg)
    return Point(p.x + length * math.cos(rad), p.y + length * math.sin(rad))


def apply_seam_allowance(points: list[Point], allowance_cm: float) -> list[Point]:
    """Offset polygon outward by allowance_cm (simple normal expansion)."""
    n = len(points)
    result = []
    for i in range(n):
        a = points[(i - 1) % n]
        b = points[i]
        c = points[(i + 1) % n]
        ab = sub(b, a)
        bc = sub(c, b)
        len_ab = math.hypot(*ab) or 1
        len_bc = math.hypot(*bc) or 1
        normal_ab = Point(-ab.y / len_ab, ab.x / len_ab)
        normal_bc = Point(-bc.y / len_bc, bc.x / len_bc)
        bisector = Point(
            (normal_ab.x + normal_bc.x) / 2,
            (normal_ab.y + normal_bc.y) / 2,
        )
        blen = math.hypot(*bisector) or 1
        result.append(Point(
            b.x + allowance_cm * bisector.x / blen,
            b.y + allowance_cm * bisector.y / blen,
        ))
    return result
