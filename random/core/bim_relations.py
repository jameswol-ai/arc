def connect_rooms_to_structure(bim_model):
    room_ids = [eid for eid, e in bim_model.elements.items() if e.element_type == "room"]
    column_ids = [eid for eid, e in bim_model.elements.items() if e.element_type == "column"]

    for r in room_ids:
        for c in column_ids:
            bim_model.link(r, c)
