from dataclasses import dataclass, field
from typing import List, Dict, Any
import uuid

# =========================================================
# 🧱 BIM DIGITAL TWIN CORE MODEL
# =========================================================

@dataclass
class BIMElement:
    id: str
    element_type: str   # beam, column, slab, wall, room
    properties: Dict[str, Any]
    geometry: Dict[str, Any]
    relations: List[str] = field(default_factory=list)


@dataclass
class BIMModel:
    building_id: str
    elements: Dict[str, BIMElement] = field(default_factory=dict)

    def add_element(self, element: BIMElement):
        self.elements[element.id] = element

    def link(self, id_a: str, id_b: str):
        if id_a in self.elements:
            self.elements[id_a].relations.append(id_b)

    def get_element(self, element_id: str):
        return self.elements.get(element_id)
