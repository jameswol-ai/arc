"""Reusable version-history helpers for the Arc Streamlit application."""
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List


def build_version(asset: Dict[str, Any]) -> Dict[str, Any]:
    """Create a serialisable library record from a generated design asset."""
    return {
        "id": asset.get("id"),
        "type": asset.get("type"),
        "country": asset.get("country"),
        "soil": asset.get("soil_name"),
        "total_gfa": asset.get("total_gfa", 0),
        "scores": deepcopy(asset.get("scores", {})),
        "plan": deepcopy(asset.get("plan", asset.get("rooms", []))),
        "timestamp": datetime.now().isoformat(),
    }


def save_version(mem: Dict[str, Any], asset: Dict[str, Any]) -> Dict[str, Any]:
    """Append a design version to memory and return the new record."""
    versions: List[Dict[str, Any]] = list(mem.get("designs", []))
    version = build_version(asset)
    versions.append(version)
    mem["designs"] = versions
    return version


def get_versions(mem: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return saved design versions without mutating the supplied memory."""
    return list(mem.get("designs", []))
