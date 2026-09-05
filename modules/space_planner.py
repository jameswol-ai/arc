"""Metric-aware generative space planning for Arc.

This module turns the preliminary metric rules into a deterministic planning
layer. It generates dimensioned room candidates, applies circulation and floor
plate constraints, scores adjacency, and selects the strongest candidate.

The rules are intentionally transparent and preliminary. They are not a
substitute for an adopted local code, licensed Metric Design Handbook dataset,
accessibility standard, fire strategy, or professional design review.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Sequence, Tuple
import math
import random

from .metric_design import RULES, CIRCULATION_MIN_WIDTH, MAIN_CORRIDOR_TARGET_WIDTH


@dataclass(frozen=True)
class RoomSpec:
    room_type: str
    min_area: float
    target_area: float
    min_width: float
    max_aspect: float


DEFAULT_TARGET_MULTIPLIER = 1.20
CIRCULATION_RATIO = 0.16
CORE_RATIO = 0.10
PLANNING_TOLERANCE = 0.08

ADJACENCY_PREFERENCES: Dict[str, Tuple[str, ...]] = {
    "Living Room": ("Dining Room", "Kitchen"),
    "Dining Room": ("Living Room", "Kitchen"),
    "Kitchen": ("Dining Room", "Living Room", "Storage"),
    "Bedroom": ("Bathroom", "Ensuite", "Corridor"),
    "Bathroom": ("Bedroom", "Corridor"),
    "Ensuite": ("Bedroom",),
    "Office": ("Corridor", "Conference"),
    "Conference": ("Office", "Corridor"),
    "Storage": ("Kitchen", "Corridor", "Loading Bay"),
    "Manufacturing": ("Loading Bay", "Storage"),
    "Loading Bay": ("Manufacturing", "Storage"),
}


def room_spec(room_type: str, target_multiplier: float = DEFAULT_TARGET_MULTIPLIER) -> RoomSpec | None:
    rule = RULES.get(room_type)
    if not rule:
        return None
    minimum = float(rule["min_area"])
    target = minimum * max(1.0, float(target_multiplier))
    return RoomSpec(room_type, minimum, target, float(rule["min_width"]), float(rule["max_aspect"]))


def _balanced_dimensions(area: float, min_width: float, max_aspect: float) -> Tuple[float, float]:
    area = max(area, min_width * min_width)
    width = max(math.sqrt(area), min_width)
    length = area / width
    if length / width > max_aspect:
        width = max(math.sqrt(area / max_aspect), min_width)
        length = area / width
    if width > length:
        width, length = length, width
    return round(width, 2), round(length, 2)


def generate_room_candidate(room_type: str, rng: random.Random, target_multiplier: float = DEFAULT_TARGET_MULTIPLIER) -> Dict[str, Any] | None:
    spec = room_spec(room_type, target_multiplier)
    if spec is None:
        return None
    target = spec.target_area * rng.uniform(0.92, 1.10)
    width, length = _balanced_dimensions(target, spec.min_width, spec.max_aspect)
    if rng.random() < 0.5:
        width, length = round(length, 2), round(width, 2)
    return {
        "type": room_type,
        "w": width,
        "h": length,
        "area": round(width * length, 2),
        "metric_target_area": round(spec.target_area, 2),
        "metric_min_area": round(spec.min_area, 2),
        "metric_min_width": round(spec.min_width, 2),
    }


def _floor_plate(plot_size: float, rng: random.Random) -> Tuple[float, float, float]:
    coverage = rng.uniform(0.50, 0.70)
    floor_area = max(100.0, plot_size * coverage)
    aspect = rng.uniform(1.15, 1.65)
    width = math.sqrt(floor_area / aspect)
    depth = floor_area / width
    return round(width, 2), round(depth, 2), round(floor_area, 2)


def _bbox_overlap(a: Dict[str, Any], b: Dict[str, Any], gap: float = 0.05) -> bool:
    return not (
        a["x"] + a["w"] + gap <= b["x"]
        or b["x"] + b["w"] + gap <= a["x"]
        or a["y"] + a["h"] + gap <= b["y"]
        or b["y"] + b["h"] + gap <= a["y"]
    )


def _place_rooms(rooms: Sequence[Dict[str, Any]], plate_w: float, plate_d: float, rng: random.Random) -> Tuple[List[Dict[str, Any]], bool]:
    placed: List[Dict[str, Any]] = []
    cursor_x = cursor_y = row_depth = 0.0
    ordered = sorted(rooms, key=lambda r: r["w"] * r["h"], reverse=True)
    for source in ordered:
        room = dict(source)
        w, h = float(room["w"]), float(room["h"])
        if cursor_x + w > plate_w:
            cursor_x = 0.0
            cursor_y += row_depth + 0.25
            row_depth = 0.0
        if cursor_y + h > plate_d:
            w, h = h, w
            if cursor_x + w > plate_w:
                cursor_x = 0.0
                cursor_y += row_depth + 0.25
                row_depth = 0.0
            if cursor_y + h > plate_d:
                return [], False
        room["w"], room["h"] = round(w, 2), round(h, 2)
        room["x"], room["y"] = round(cursor_x, 2), round(cursor_y, 2)
        placed.append(room)
        cursor_x += w + 0.25
        row_depth = max(row_depth, h)
    for i, room in enumerate(placed):
        if room["x"] + room["w"] > plate_w + PLANNING_TOLERANCE or room["y"] + room["h"] > plate_d + PLANNING_TOLERANCE:
            return [], False
        for other in placed[i + 1:]:
            if _bbox_overlap(room, other):
                return [], False
    return placed, True


def _adjacency_score(rooms: Iterable[Dict[str, Any]]) -> float:
    """Score preferred adjacency without assuming coordinates on legacy rooms.

    Fallback and imported plans may contain room dictionaries without x/y.
    Those rooms are still valid for area/program analysis, but they cannot
    contribute a geometric adjacency score until placed.
    """
    items = list(rooms)
    if len(items) < 2:
        return 0.0

    score = 0.0
    opportunities = 0
    for room in items:
        preferred = set(ADJACENCY_PREFERENCES.get(room.get("type", ""), ()))
        if not preferred:
            continue
        opportunities += 1

        # Only geometrically score rooms that have complete placement data.
        if any(key not in room for key in ("x", "y", "w", "h")):
            continue
        try:
            cx = float(room["x"]) + float(room["w"]) / 2.0
            cy = float(room["y"]) + float(room["h"]) / 2.0
        except (TypeError, ValueError):
            continue

        best = 0.0
        for other in items:
            if other is room or other.get("type") not in preferred:
                continue
            if any(key not in other for key in ("x", "y", "w", "h")):
                continue
            try:
                ox = float(other["x"]) + float(other["w"]) / 2.0
                oy = float(other["y"]) + float(other["h"]) / 2.0
            except (TypeError, ValueError):
                continue
            best = max(best, 1.0 / (1.0 + math.hypot(cx - ox, cy - oy)))
        score += best

    return round(score / opportunities * 100, 1) if opportunities else 0.0


def _candidate_score(rooms: Sequence[Dict[str, Any]], plate_area: float, floor_area: float, domain: str) -> float:
    room_area = sum(float(r["w"]) * float(r["h"]) for r in rooms)
    efficiency = room_area / floor_area * 100 if floor_area else 0.0
    efficiency_score = max(0.0, 100.0 - abs(efficiency - 72.0) * 2.0)
    adjacency = _adjacency_score(rooms)
    fit = max(0.0, min(100.0, room_area / plate_area * 100.0)) if plate_area else 0.0
    domain_bonus = 0.0
    if domain == "Industrial" and any(r["type"] == "Manufacturing" for r in rooms):
        domain_bonus += 5.0
    if domain == "Commercial" and any(r["type"] == "Conference" for r in rooms):
        domain_bonus += 3.0
    if domain == "Residential" and any(r["type"] == "Living Room" for r in rooms):
        domain_bonus += 3.0
    return round(efficiency_score * 0.45 + adjacency * 0.35 + fit * 0.20 + domain_bonus, 2)


def _fallback_plan(domain: str, plate_w: float, plate_d: float, floor_area: float, baths: int) -> Dict[str, Any]:
    """Return a guaranteed renderer-safe and scorer-safe fallback."""
    min_w = max(CIRCULATION_MIN_WIDTH, MAIN_CORRIDOR_TARGET_WIDTH)
    corridor_h = max(6.0, min(plate_d * 0.20, floor_area * CIRCULATION_RATIO / min_w))
    rooms: List[Dict[str, Any]] = [
        {
            "name": "Metric Main Corridor",
            "type": "Corridor",
            "w": round(min_w, 2),
            "h": round(corridor_h, 2),
            "area": round(min_w * corridor_h, 2),
        }
    ]

    core_area = max(14.0, min(floor_area * CORE_RATIO, max(14.0, plate_w * plate_d * 0.12)))
    core_w = max(1.2, min(3.0, math.sqrt(core_area)))
    core_h = round(core_area / core_w, 2)
    rooms.append(
        {
            "name": "Metric Stair Core",
            "type": "Stairs",
            "w": round(core_w, 2),
            "h": core_h,
            "area": round(core_w * core_h, 2),
        }
    )

    defaults = {"Residential": "Living Room", "Commercial": "Office", "Industrial": "Manufacturing"}
    fallback_type = defaults.get(domain, "Office")
    spec = room_spec(fallback_type)
    if spec:
        w, h = _balanced_dimensions(spec.target_area, spec.min_width, spec.max_aspect)
        rooms.append(
            {
                "name": f"{fallback_type} 1",
                "type": fallback_type,
                "w": w,
                "h": h,
                "area": round(w * h, 2),
            }
        )

    for index in range(max(0, int(baths))):
        spec = room_spec("Bathroom")
        w, h = _balanced_dimensions(
            spec.target_area if spec else 4.2,
            spec.min_width if spec else 1.5,
            spec.max_aspect if spec else 2.5,
        )
        rooms.append(
            {
                "name": f"Bathroom {index + 1}",
                "type": "Bathroom",
                "w": w,
                "h": h,
                "area": round(w * h, 2),
            }
        )

    # Try to place the fallback so downstream renderers and geometric scoring
    # receive the same x/y contract as normal generated plans.
    placed, ok = _place_rooms(rooms, max(plate_w, 12.0), max(plate_d, 12.0), random.Random(0))
    if ok:
        rooms = placed
    else:
        # Absolute last-resort placement: sequential, non-overlapping anchors.
        # This guarantees x/y for every room even when the fallback plate is
        # smaller than the requested program.
        x = y = 0.0
        for room in rooms:
            room["x"] = round(x, 2)
            room["y"] = round(y, 2)
            x += float(room["w"]) + 0.25
            if x > max(plate_w, 12.0):
                x = 0.0
                y += max(float(room["h"]), 1.0) + 0.25

    return {
        "rooms": rooms,
        "plate_width": plate_w,
        "plate_depth": plate_d,
        "floor_area": floor_area,
        "metric_planning_score": round(_candidate_score(rooms, plate_w * plate_d, floor_area, domain), 2),
        "candidate_index": -1,
        "generated_candidates": 0,
        "planning": {
            "space_efficiency_target_pct": 72.0,
            "circulation_ratio": CIRCULATION_RATIO,
            "core_ratio": CORE_RATIO,
            "adjacency_score": _adjacency_score(rooms),
            "room_program_count": len(rooms),
            "bathroom_count": sum(r["type"] == "Bathroom" for r in rooms),
            "planning_engine": "metric-aware-v1",
            "status": "FALLBACK",
        },
    }


def generate_metric_plan(
    domain: str,
    plot_size: float,
    floors: int,
    room_types: Sequence[str] | None,
    baths: int = 0,
    seed: int = 0,
    candidates: int = 8,
) -> Dict[str, Any]:
    rng = random.Random(seed)
    plate_w, plate_d, floor_area = _floor_plate(float(plot_size), rng)
    requested = [str(x) for x in (room_types or []) if str(x) in RULES]
    if not requested:
        requested = ["Living Room", "Kitchen", "Bedroom", "Bathroom"] if domain == "Residential" else ["Office", "Conference", "Storage"]
    requested = [x for x in requested if x != "Bathroom"]
    requested.extend(["Bathroom"] * max(0, int(baths)))
    base_specs = list(requested)
    if domain == "Residential" and "Living Room" not in base_specs:
        base_specs.append("Living Room")
    if domain == "Commercial" and "Office" not in base_specs:
        base_specs.append("Office")
    if domain == "Industrial" and "Manufacturing" not in base_specs:
        base_specs.append("Manufacturing")

    best: Dict[str, Any] | None = None
    generated = 0
    for candidate_index in range(max(1, int(candidates))):
        candidate_rng = random.Random(rng.randint(0, 10**9) + candidate_index)
        room_program: List[Dict[str, Any]] = []
        for room_type in base_specs:
            room = generate_room_candidate(room_type, candidate_rng)
            if room:
                room["name"] = f"{room_type} {sum(1 for x in room_program if x['type'] == room_type) + 1}"
                room_program.append(room)

        corridor_width = max(CIRCULATION_MIN_WIDTH, MAIN_CORRIDOR_TARGET_WIDTH)
        corridor_area = max(5.0, floor_area * CIRCULATION_RATIO)
        room_program.append(
            {
                "name": "Metric Main Corridor",
                "type": "Corridor",
                "w": round(corridor_width, 2),
                "h": round(corridor_area / corridor_width, 2),
                "area": round(corridor_area, 2),
            }
        )
        stair_area = max(14.0, floor_area * CORE_RATIO)
        stair_width = max(1.2, min(3.0, math.sqrt(stair_area)))
        room_program.append(
            {
                "name": "Metric Stair Core",
                "type": "Stairs",
                "w": round(stair_width, 2),
                "h": round(stair_area / stair_width, 2),
                "area": round(stair_area, 2),
            }
        )

        placed, success = _place_rooms(room_program, plate_w, plate_d, candidate_rng)
        if not success:
            continue
        generated += 1
        score = _candidate_score(placed, plate_w * plate_d, floor_area, domain)
        candidate = {
            "rooms": placed,
            "plate_width": plate_w,
            "plate_depth": plate_d,
            "floor_area": floor_area,
            "metric_planning_score": score,
            "candidate_index": candidate_index,
            "generated_candidates": generated,
            "planning": {
                "space_efficiency_target_pct": 72.0,
                "circulation_ratio": CIRCULATION_RATIO,
                "core_ratio": CORE_RATIO,
                "adjacency_score": _adjacency_score(placed),
                "room_program_count": len(placed),
                "bathroom_count": sum(1 for room in placed if room.get("type") == "Bathroom"),
                "planning_engine": "metric-aware-v1",
            },
        }
        if best is None or score > best["metric_planning_score"]:
            best = candidate

    if best is None:
        return _fallback_plan(domain, plate_w, plate_d, floor_area, baths)
    best["generated_candidates"] = generated
    return best
