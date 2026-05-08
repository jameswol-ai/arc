import json
from datetime import datetime


# =========================================================
# 🏗️ BIM EXPORTER (DIGITAL TWIN → EXTERNAL FORMAT)
# Converts internal BIM graph into IFC-like structured JSON
# =========================================================

def export_bim(bim_model, include_metadata=True, pretty=True):
    """
    Exports BIMModel into a structured digital twin format.

    This is NOT full IFC compliance, but an IFC-inspired schema:
    - element-based
    - relationship-aware
    - metadata traceable
    """

    elements = {}

    for eid, element in bim_model.elements.items():
        elements[eid] = {
            "type": element.element_type,
            "properties": element.properties,
            "geometry": element.geometry,
            "relations": element.relations
        }

    export_data = {
        "schema": "RANDOM_BIM_v1",
        "building_id": getattr(bim_model, "building_id", None),
        "elements": elements
    }

    # =========================================================
    # OPTIONAL METADATA (TRACEABILITY + DIGITAL TWIN VERSIONING)
    # =========================================================
    if include_metadata:
        export_data["metadata"] = {
            "export_time": datetime.utcnow().isoformat(),
            "element_count": len(elements),
            "format": "json_ifc_like",
            "system": "RANDOM_AEC_ENGINE"
        }

    # =========================================================
    # SERIALIZATION
    # =========================================================
    if pretty:
        return json.dumps(export_data, indent=2)
    else:
        return json.dumps(export_data)
