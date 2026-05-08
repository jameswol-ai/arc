import json

def export_bim(bim_model):
    data = {
        "building_id": bim_model.building_id,
        "elements": {}
    }

    for eid, element in bim_model.elements.items():
        data["elements"][eid] = {
            "type": element.element_type,
            "properties": element.properties,
            "geometry": element.geometry,
            "relations": element.relations
        }

    return json.dumps(data, indent=2)
