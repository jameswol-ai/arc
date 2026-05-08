from dataclasses import dataclass, field
from typing import List, Dict, Any

# =========================
# 🏗️ CORE BUILDING OBJECT
# =========================

@dataclass
class Building:
    name: str
    building_type: str
    floors: int
    site_area: float
    grid: Dict[str, Any] = field(default_factory=dict)
    architecture: Dict[str, Any] = field(default_factory=dict)
    structure: Dict[str, Any] = field(default_factory=dict)
    mep: Dict[str, Any] = field(default_factory=dict)
    cost: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Floor:
    level: int
    rooms: List[Dict[str, Any]]
    circulation: Dict[str, Any]

@dataclass
class StructuralElement:
    element_type: str  # beam, column, slab
    position: List[float]
    load_capacity: float
    material: str

@dataclass
class LoadCase:
    dead_load: float
    live_load: float
    wind_load: float
    seismic_load: float
