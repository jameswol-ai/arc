import uuid
from core.bim_model import BIMModel, BIMElement


def build_bim_model(architecture, structure):
    model = BIMModel(building_id=str(uuid.uuid4()))

    # =========================
    # ROOMS → BIM ELEMENTS
    # =========================
    for room in architecture["rooms"]:
        element = BIMElement(
            id=str(uuid.uuid4()),
            element_type="room",
            properties=room,
            geometry={"type": "polygon", "area": room.get("area", 20)}
        )
        model.add_element(element)

    # =========================
    # COLUMNS → BIM ELEMENTS
    # =========================
    for i in range(10):  # simplified placeholder
        element = BIMElement(
            id=f"column-{i}",
            element_type="column",
            properties={"material": "concrete"},
            geometry={"height": 3.2}
        )
        model.add_element(element)

    # =========================
    # STRUCTURAL STATUS NODE
    # =========================
    model.add_element(
        BIMElement(
            id="structure-summary",
            element_type="analysis",
            properties=structure,
            geometry={}
        )
    )

    return model
