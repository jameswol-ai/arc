from copy import deepcopy


# =========================================================
# 🧬 PARAMETRIC BIM ENGINE
# Updates BIM model when key parameters change
# =========================================================

class ParametricEngine:

    def __init__(self, bim_model):
        self.bim = bim_model
        self.parameters = {
            "floor_height": 3.2,
            "grid_spacing": 4.0,
            "wall_thickness": 0.2
        }

    # -------------------------
    # UPDATE PARAMETER
    # -------------------------
    def set_parameter(self, key, value):
        self.parameters[key] = value
        self.recompute()

    # -------------------------
    # CORE RECOMPUTE LOGIC
    # -------------------------
    def recompute(self):
        """
        Rebuild dependent BIM elements when parameters change.
        """

        for eid, element in self.bim.elements.items():

            # FLOOR HEIGHT PROPAGATION
            if element.element_type == "column":
                floors = element.properties.get("floors", 1)
                element.geometry["height"] = floors * self.parameters["floor_height"]

            # GRID PROPAGATION
            if element.element_type == "beam":
                element.geometry["span"] = self.parameters["grid_spacing"]

            # ROOM THICKNESS ADJUSTMENT
            if element.element_type == "wall":
                element.properties["thickness"] = self.parameters["wall_thickness"]

        return self.bim

    # -------------------------
    # SNAPSHOT (SAFE COPY)
    # -------------------------
    def get_model(self):
        return deepcopy(self.bim)
