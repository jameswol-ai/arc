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
    """Return a centralized metric planning specification for a room type."""
    rule = RULES.get(room_type)
    if not rule:
        return None
    minimum = float(rule["min_area"])
    target = minimum * max(1.0, float(target_multiplier))
    return RoomSpec(
        room_type=room_type,
        min_area=minimum,
        target_area=target,
        min_width=float(rule["min_width"]),
        max_aspect=float(rule["max_aspect"]),
    )


def _balanced_dimensions(area: float, min_width: float, max_aspect: float) -> Tuple[float, float]:
    """Find compact dimensions satisfying minimum width and aspect constraints."""
    area = max(area, min_width * min_width)
    width = math.sqrt(area)
    width = max(width, min_width)
    length = area / width

    if length / width > max_aspect:
        width = math.sqrt(area / max_aspect)
        width = max(width, min_width)
        length = area / width

    if width > length:
        width, length = length, width

    return round(width, 2), round(length, 2)


def generate_room_candidate(
    room_type: str,
    rng: random.Random,
    target_multiplier: float = DEFAULT_TARGET_MULTIPLIER,
) -> Dict[str, Any] | None:
    """Generate one metric-aware dimensioned room candidate."""
    spec = room_spec(room_type, target_multiplier)
    if spec is None:
        return None

    target = spec.target_area * rng.uniform(0.92, 1.10)
    width, length = _balanced_dimensions(target, spec.min_width, spec.max_aspect)

    # Small controlled variation keeps concepts distinct without breaking the
    # dimensional rules.
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
    """Create a plausible rectangular floor plate from plot area."""
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


def _place_rooms(
    rooms: Sequence[Dict[str, Any]],
    plate_w: float,
    plate_d: float,
    rng: random.Random,
) -> Tuple[List[Dict[str, Any]], bool]:
    """Place rooms using a simple deterministic shelf/bin-packing strategy."""
    placed: List[Dict[str, Any]] = []
    cursor_x = 0.0
    cursor_y = 0.0
    row_depth = 0.0

    ordered = sorted(rooms, key=lambda r: r["w"] * r["h"], reverse=True)

    for source in ordered:
        room = dict(source)
        w, h = float(room["w"]), float(room["h"])

        if cursor_x + w > plate_w:
            cursor_x = 0.0
            cursor_y += row_depth + 0.25
            row_depth = 0.0

        if cursor_y + h > plate_d:
            # Try a rotated orientation before declaring failure.
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

    # Confirm there are no overlaps after placement.
    for i, room in enumerate(placed):
        if room["x"] + room["w"] > plate_w + PLANNING_TOLERANCE:
            return [], False
        if room["y"] + room["h"] > plate_d + PLANNING_TOLERANCE:
            return [], False
        for other in placed[i + 1 :]:
            if _bbox_overlap(room, other):
                return [], False

    return placed, True


def _adjacency_score(rooms: Iterable[Dict[str, Any]]) -> float:
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
        best = 0.0
        cx = room["x"] + room["w"] / 2
        cy = room["y"] + room["h"] / 2
        for other in items:
            if other is room or other.get("type") not in preferred:
                continue
            ox = other["x"] + other["w"] / 2
            oy = other["y"] + other["h"] / 2
            distance = math.hypot(cx - ox, cy - oy)
            best = max(best, 1.0 / (1.0 + distance))
        score += best
    return round(score / opportunities * 100, 1) if opportunities else 0.0


def _candidate_score(
    rooms: Sequence[Dict[str, Any]],
    plate_area: float,
    floor_area: float,
    domain: str,
) -> float:
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


def generate_metric_plan(
    domain: str,
    plot_size: float,
    floors: int,
    room_types: Sequence[str] | None,
    seed: int = 0,
    candidates: int = 8,
) -> Dict[str, Any]:
    """Generate and select the strongest metric-aware spatial candidate."""
    rng = random.Random(seed)
    plate_w, plate_d, floor_area = _floor_plate(float(plot_size), rng)

    requested = [str(x) for x in (room_types or []) if str(x) in RULES]
    if not requested:
        requested = ["Living Room", "Kitchen", "Bedroom", "Bathroom"] if domain == "Residential" else ["Office", "Conference", "Storage"]

    base_specs: List[str] = list(requested)
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
        corridor = {
            "name": "Metric Main Corridor",
            "type": "Corridor",
            "w": round(corridor_width, 2),
            "h": round(corridor_area / corridor_width, 2),
            "area": round(corridor_area, 2),
        }
        room_program.append(corridor)

        stair_area = max(14.0, floor_area * CORE_RATIO)
        stair_width = max(1.2, min(3.0, math.sqrt(stair_area)))
        room_program.append({
            "name": "Metric Stair Core",
            "type": "Stairs",
            "w": round(stair_width, 2),
            "h": round(stair_area / stair_width, 2),
            "area": round(stair_area, 2),
        })

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
                "planning_engine": "metric-aware-v1",
            },
        }
        if best is None or score > best["metric_planning_score"]:
            best = candidate

    if best is None:
        return {
            "rooms": [],
            "plate_width": plate_w,
            "plate_depth": plate_d,
            "floor_area": floor_area,
            "metric_planning_score": 0.0,
            "generated_candidates": 0,
            "planning": {
                "planning_engine": "metric-aware-v1",
                "status": "INFEASIBLE",
            },
        }

    best["generated_candidates"] = generated
    return best
