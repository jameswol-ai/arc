# floorplan_engine.py
# =========================================================
# 🧠 RANDOM AI — FLOORPLAN GENERATION ENGINE
# Rule-based spatial layout system with structural intent
# =========================================================

import random
import math
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple, Optional

# =========================================================
# 🧱 CORE DATA STRUCTURES
# =========================================================

@dataclass
class Room:
    name: str
    width: float
    length: float
    floor: int
    x: float = 0
    y: float = 0
    zone: str = "residential"

    def area(self):
        return self.width * self.length


@dataclass
class FloorPlan:
    floor_index: int
    width: float
    length: float
    rooms: List[Room]


@dataclass
class BuildingModel:
    name: str
    floors: List[FloorPlan]
    grid_spacing: float
    building_type: str


# =========================================================
# 🧭 ROOM LIBRARY (ZONED BEHAVIOR)
# =========================================================

ROOM_LIBRARY = {
    "residential": [
        ("Living Room", 6, 5),
        ("Kitchen", 4, 4),
        ("Bedroom", 5, 4),
        ("Bathroom", 3, 2),
        ("Dining", 4, 4),
    ],
    "commercial": [
        ("Office", 5, 4),
        ("Meeting Room", 6, 5),
        ("Lobby", 8, 6),
        ("Workstation Area", 10, 6),
        ("Storage", 4, 3),
    ],
    "industrial": [
        ("Workshop", 12, 8),
        ("Storage Bay", 10, 6),
        ("Control Room", 5, 4),
        ("Loading Area", 14, 10),
    ]
}


# =========================================================
# 🧠 FLOORPLAN ENGINE
# =========================================================

class FloorPlanEngine:

    def __init__(self, grid_spacing: float = 3.0):
        self.grid_spacing = grid_spacing

    # -----------------------------
    # MAIN GENERATION ENTRY POINT
    # -----------------------------
    def generate_building(
        self,
        building_type: str = "residential",
        floors: int = 2,
        floor_width: float = 20,
        floor_length: float = 15
    ) -> BuildingModel:

        model_floors = []

        for i in range(floors):
            floor = self._generate_floor(
                floor_index=i,
                building_type=building_type,
                width=floor_width,
                length=floor_length
            )
            model_floors.append(floor)

        return BuildingModel(
            name=f"{building_type.upper()}_BLOCK",
            floors=model_floors,
            grid_spacing=self.grid_spacing,
            building_type=building_type
        )

    # -----------------------------
    # SINGLE FLOOR GENERATION
    # -----------------------------
    def _generate_floor(
        self,
        floor_index: int,
        building_type: str,
        width: float,
        length: float
    ) -> FloorPlan:

        rooms = self._generate_rooms(building_type, floor_index)

        self._apply_grid_layout(rooms, width, length)
        self._apply_adjacency_rules(rooms, building_type)

        return FloorPlan(
            floor_index=floor_index,
            width=width,
            length=length,
            rooms=rooms
        )

    # -----------------------------
    # ROOM CREATION
    # -----------------------------
    def _generate_rooms(self, building_type: str, floor_index: int) -> List[Room]:
        base_rooms = ROOM_LIBRARY.get(building_type, ROOM_LIBRARY["residential"])

        rooms = []
        for name, w, l in base_rooms:
            # stochastic variation for realism
            width = w * random.uniform(0.9, 1.15)
            length = l * random.uniform(0.9, 1.15)

            rooms.append(Room(
                name=name,
                width=round(width, 2),
                length=round(length, 2),
                floor=floor_index,
                zone=building_type
            ))

        return rooms

    # -----------------------------
    # GRID-BASED LAYOUT ENGINE
    # -----------------------------
    def _apply_grid_layout(self, rooms: List[Room], width: float, length: float):

        grid_x = 0
        grid_y = 0

        max_row_height = 0

        for room in rooms:
            # snap to grid
            room.x = self._snap(grid_x)
            room.y = self._snap(grid_y)

            grid_x += room.width + self.grid_spacing
            max_row_height = max(max_row_height, room.length)

            # wrap row if overflow
            if grid_x > width:
                grid_x = 0
                grid_y += max_row_height + self.grid_spacing
                max_row_height = 0

    # -----------------------------
    # ADJACENCY INTELLIGENCE
    # -----------------------------
    def _apply_adjacency_rules(self, rooms: List[Room], building_type: str):

        # Simple heuristic rules
        if building_type == "residential":
            self._try_adjacent(rooms, "Kitchen", "Dining")
            self._try_adjacent(rooms, "Bedroom", "Bathroom")

        elif building_type == "commercial":
            self._try_adjacent(rooms, "Office", "Meeting Room")
            self._try_adjacent(rooms, "Lobby", "Workstation Area")

        elif building_type == "industrial":
            self._try_adjacent(rooms, "Workshop", "Storage Bay")

    def _try_adjacent(self, rooms: List[Room], a: str, b: str):
        ra = next((r for r in rooms if r.name == a), None)
        rb = next((r for r in rooms if r.name == b), None)

        if ra and rb:
            rb.x = ra.x + ra.width + 1  # forced adjacency corridor

    # -----------------------------
    # GRID SNAP HELPER
    # -----------------------------
    def _snap(self, value: float) -> float:
        return round(value / self.grid_spacing) * self.grid_spacing


# =========================================================
# 🧾 EXPORT HELPERS (for Streamlit / DXF later)
# =========================================================

def building_to_dict(model: BuildingModel) -> Dict:
    return {
        "name": model.name,
        "grid_spacing": model.grid_spacing,
        "type": model.building_type,
        "floors": [
            {
                "floor": f.floor_index,
                "width": f.width,
                "length": f.length,
                "rooms": [asdict(r) for r in f.rooms]
            }
            for f in model.floors
        ]
    }


# =========================================================
# 🧪 QUICK TEST RUN
# =========================================================

if __name__ == "__main__":
    engine = FloorPlanEngine(grid_spacing=3.0)

    building = engine.generate_building(
        building_type="residential",
        floors=3,
        floor_width=25,
        floor_length=18
    )

    print(building_to_dict(building))
