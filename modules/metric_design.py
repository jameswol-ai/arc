"""
Metric Design Intelligence for Arc.

This module provides a transparent, deterministic spatial-design validation
layer. Values are deliberately centralized so they can later be replaced or
extended with licensed/local design-handbook datasets without changing the UI.

The validator is a design-review aid, not a substitute for statutory approval,
accessibility review, fire strategy, or a qualified architect/engineer.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List


# Preliminary metric design rules. Keep these centralized and auditable.
RULES: Dict[str, Dict[str, float]] = {
    "Bedroom": {"min_area": 9.0, "min_width": 2.7, "max_aspect": 2.5},
    "Bathroom": {"min_area": 3.5, "min_width": 1.5, "max_aspect": 2.5},
    "Ensuite": {"min_area": 3.0, "min_width": 1.4, "max_aspect": 2.5},
    "Living Room": {"min_area": 16.0, "min_width": 3.5, "max_aspect": 2.5},
    "Kitchen": {"min_area": 7.0, "min_width": 2.4, "max_aspect": 2.5},
    "Dining Room": {"min_area": 10.0, "min_width": 2.7, "max_aspect": 2.5},
    "Office": {"min_area": 9.0, "min_width": 2.7, "max_aspect": 2.5},
    "Storage": {"min_area": 3.0, "min_width": 1.5, "max_aspect": 3.0},
    "Corridor": {"min_area": 5.0, "min_width": 1.2, "max_aspect": 12.0},
    "Stairs": {"min_area": 14.0, "min_width": 1.2, "max_aspect": 2.5},
    "Balcony": {"min_area": 4.0, "min_width": 1.5, "max_aspect": 4.0},
    "Conference": {"min_area": 20.0, "min_width": 3.5, "max_aspect": 2.5},
    "Manufacturing": {"min_area": 120.0, "min_width": 8.0, "max_aspect": 3.0},
    "Loading Bay": {"min_area": 45.0, "min_width": 5.0, "max_aspect": 3.0},
}

CIRCULATION_MIN_WIDTH = 1.20
MAIN_CORRIDOR_TARGET_WIDTH = 1.50
DOOR_MIN_WIDTH = 0.80
ACCESSIBLE_DOOR_TARGET = 0.90


@dataclass
class Check:
    category: str
    item: str
    status: str
    value: str
    requirement: str
    severity: str = "Info"

    def as_dict(self) -> Dict[str, str]:
        return {
            "Category": self.category,
            "Check": self.item,
            "Status": self.status,
            "Value": self.value,
            "Requirement": self.requirement,
            "Severity": self.severity,
        }


def _room_area(room: Dict[str, Any]) -> float:
    try:
        return max(0.0, float(room.get("w", 0))) * max(0.0, float(room.get("h", 0)))
    except (TypeError, ValueError):
        return 0.0


def _room_width(room: Dict[str, Any]) -> float:
    try:
        return min(abs(float(room.get("w", 0))), abs(float(room.get("h", 0))))
    except (TypeError, ValueError):
        return 0.0


def _room_aspect(room: Dict[str, Any]) -> float:
    try:
        a = abs(float(room.get("w", 0)))
        b = abs(float(room.get("h", 0)))
        return max(a, b) / min(a, b) if min(a, b) > 0 else 999.0
    except (TypeError, ValueError):
        return 999.0


def _add_room_checks(checks: List[Check], rooms: Iterable[Dict[str, Any]]) -> None:
    for room in rooms:
        room_type = str(room.get("type", "Unknown"))
        name = str(room.get("name", room_type))
        rule = RULES.get(room_type)
        if not rule:
            continue

        area = _room_area(room)
        width = _room_width(room)
        aspect = _room_aspect(room)

        checks.append(Check(
            "Space", f"{name} area", "PASS" if area >= rule["min_area"] else "FAIL",
            f"{area:.1f} m²", f">= {rule['min_area']:.1f} m²", "High" if area < rule["min_area"] else "Info"
        ))
        checks.append(Check(
            "Space", f"{name} minimum dimension", "PASS" if width >= rule["min_width"] else "REVIEW",
            f"{width:.2f} m", f">= {rule['min_width']:.2f} m", "Medium" if width < rule["min_width"] else "Info"
        ))
        checks.append(Check(
            "Space", f"{name} proportion", "PASS" if aspect <= rule["max_aspect"] else "REVIEW",
            f"1:{aspect:.2f}", f"<= 1:{rule['max_aspect']:.1f}", "Medium" if aspect > rule["max_aspect"] else "Info"
        ))


def validate_metric_design(d: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a generated Arc spatial model against preliminary metric rules."""
    checks: List[Check] = []
    rooms = d.get("rooms") or d.get("plan") or []

    _add_room_checks(checks, rooms)

    corridor_rooms = [r for r in rooms if str(r.get("type", "")).lower() == "corridor"]
    stair_rooms = [r for r in rooms if str(r.get("type", "")).lower() == "stairs"]

    for room in corridor_rooms:
        width = _room_width(room)
        checks.append(Check(
            "Circulation", f"{room.get('name', 'Corridor')} clear width",
            "PASS" if width >= CIRCULATION_MIN_WIDTH else "FAIL",
            f"{width:.2f} m", f">= {CIRCULATION_MIN_WIDTH:.2f} m", "High" if width < CIRCULATION_MIN_WIDTH else "Info"
        ))

    if not corridor_rooms:
        checks.append(Check("Circulation", "Primary corridor", "REVIEW", "Not defined", "Provide a defined circulation route", "Medium"))
    else:
        widest = max(_room_width(r) for r in corridor_rooms)
        checks.append(Check(
            "Circulation", "Main circulation target", "PASS" if widest >= MAIN_CORRIDOR_TARGET_WIDTH else "REVIEW",
            f"{widest:.2f} m", f">= {MAIN_CORRIDOR_TARGET_WIDTH:.2f} m preferred", "Medium" if widest < MAIN_CORRIDOR_TARGET_WIDTH else "Info"
        ))

    if stair_rooms:
        for room in stair_rooms:
            width = _room_width(room)
            checks.append(Check(
                "Vertical circulation", f"{room.get('name', 'Stair')} width",
                "PASS" if width >= 1.20 else "REVIEW", f"{width:.2f} m", ">= 1.20 m preliminary target", "Medium" if width < 1.20 else "Info"
            ))
    elif int(d.get("floors", 1)) > 1:
        checks.append(Check("Vertical circulation", "Stair provision", "FAIL", "No stair detected", "Provide a compliant stair/core", "High"))

    doors = int(d.get("doors", 0) or 0)
    rooms_count = len(rooms)
    checks.append(Check(
        "Openings", "Door provision", "PASS" if doors >= rooms_count else "REVIEW",
        str(doors), f">= {rooms_count} doors for {rooms_count} modeled spaces", "Medium" if doors < rooms_count else "Info"
    ))
    checks.append(Check(
        "Accessibility", "Nominal accessible door target", "REVIEW",
        f"{DOOR_MIN_WIDTH:.2f} m baseline", f"Use >= {ACCESSIBLE_DOOR_TARGET:.2f} m where accessibility requires it", "Medium"
    ))

    floor_area = float(d.get("floor_area", 0) or 0)
    total_gfa = float(d.get("total_gfa", 0) or 0)
    plot_size = float(d.get("plot_size", 0) or 0)
    floors = max(1, int(d.get("floors", 1) or 1))

    modeled_room_area = sum(_room_area(r) for r in rooms)
    efficiency = modeled_room_area / floor_area * 100 if floor_area > 0 else 0.0
    coverage = floor_area / plot_size * 100 if plot_size > 0 else 0.0

    checks.append(Check(
        "Planning", "Modeled space efficiency", "PASS" if 45 <= efficiency <= 90 else "REVIEW",
        f"{efficiency:.1f}%", "45–90% of floor plate represented by modeled spaces", "Medium" if not 45 <= efficiency <= 90 else "Info"
    ))
    checks.append(Check(
        "Planning", "Site coverage", "PASS" if 30 <= coverage <= 75 else "REVIEW",
        f"{coverage:.1f}%", "30–75% preliminary range", "Medium" if not 30 <= coverage <= 75 else "Info"
    ))

    span = float((d.get("structural") or {}).get("span", 0) or 0)
    checks.append(Check(
        "Structure", "Typical structural span", "PASS" if 3.0 <= span <= 12.0 else "REVIEW",
        f"{span:.2f} m", "3.0–12.0 m design-review range", "Medium" if not 3.0 <= span <= 12.0 else "Info"
    ))

    fail_count = sum(c.status == "FAIL" for c in checks)
    review_count = sum(c.status == "REVIEW" for c in checks)
    pass_count = sum(c.status == "PASS" for c in checks)
    total = len(checks) or 1

    # Failures carry more weight than reviews. This score is intentionally transparent.
    score = max(0, min(100, round((pass_count + review_count * 0.5) / total * 100 - fail_count * 5)))
    if fail_count:
        status = "FAIL"
    elif review_count:
        status = "REVIEW"
    else:
        status = "PASS"

    errors = [c.as_dict() for c in checks if c.status == "FAIL"]
    warnings = [c.as_dict() for c in checks if c.status == "REVIEW"]

    return {
        "score": score,
        "status": status,
        "checks": [c.as_dict() for c in checks],
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "total": total,
            "pass": pass_count,
            "review": review_count,
            "fail": fail_count,
            "modeled_room_area_m2": round(modeled_room_area, 2),
            "space_efficiency_pct": round(efficiency, 1),
            "site_coverage_pct": round(coverage, 1),
            "floors": floors,
            "total_gfa_m2": round(total_gfa, 2),
        },
    }
