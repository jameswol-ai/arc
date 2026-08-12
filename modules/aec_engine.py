# modules/aec_engine.py (excerpt – replace the function)

def generate_spatial_model(domain, btype, plot_size, floors, baths, country, soil_name, room_types=None, seed=0):
    rng = random.Random(seed)
    plot = max(200, plot_size + rng.randint(-300, 300))
    max_fp = int(plot * rng.uniform(0.5, 0.75))
    fa = min(max_fp, rng.randint(100, int(max_fp * 1.3)))
    gfa = fa * floors
    span = 6.0 if domain == "Residential" else (7.5 if domain == "Commercial" else 12.0)
    span *= rng.uniform(0.85, 1.15)
    cols = max(8, int((fa / (span * 5.0)) * rng.uniform(3, 5)))
    beams = int(cols * rng.uniform(1.5, 2.2))
    foundation = rng.choice(FOUNDATION_TYPES.get(domain, ["Strip Footing"]))
    slab_system = rng.choice(SLAB_SYSTEMS.get(domain, ["Flat Slab"]))
    storey_height = rng.uniform(3.0, 4.2)
    wall_type = "Reinforced Concrete" if rng.random() > 0.3 else "Masonry"

    # ─── Base fixed rooms ────────────────────────────────────
    rooms = [
        {"name": "Central Corridor Gallery", "type": "Corridor", "w": 2.5, "h": 14.0, "color": "#3a3a4a"},
        {"name": "Main Staircase Core", "type": "Stairs", "w": 4.5, "h": 4.0, "color": "#4a4a5a"},
    ]

    # ─── User‑selected room types ────────────────────────────
    # Define default room types if none given
    if not room_types:
        room_types = []
    # Map type to display name and default sizes
    room_type_map = {
        "Bedroom": {"w": (4, 5), "h": (3.5, 4.5), "color": "#2a1a3a"},
        "Bathroom": {"w": (2.5, 3.5), "h": (2, 3), "color": "#4a2a2a"},
        "Ensuite": {"w": (2.5, 3.0), "h": (2, 2.5), "color": "#3a2a3a"},
        "Corridor": {"w": (2.0, 3.0), "h": (3.0, 5.0), "color": "#3a3a4a"},
        "Balcony": {"w": (2.0, 3.5), "h": (3.0, 5.0), "color": "#4a4a3a"},
        "Living Room": {"w": (6, 8), "h": (5, 6), "color": "#2a2a3a"},
        "Kitchen": {"w": (4, 5), "h": (3.5, 4.5), "color": "#1a2a1a"},
        "Dining Room": {"w": (4, 6), "h": (4, 5), "color": "#3a2a2a"},
        "Office": {"w": (4, 5), "h": (4, 5), "color": "#2a3a3a"},
        "Storage": {"w": (2, 3), "h": (2, 3), "color": "#3a3a2a"},
    }

    # Ensure at least one of each selected type appears
    for room_type in room_types:
        if room_type in room_type_map:
            specs = room_type_map[room_type]
            w = rng.uniform(specs["w"][0], specs["w"][1])
            h = rng.uniform(specs["h"][0], specs["h"][1])
            rooms.append({
                "name": f"{room_type} {len([r for r in rooms if r['type'] == room_type]) + 1}",
                "type": room_type,
                "w": round(w, 2),
                "h": round(h, 2),
                "color": specs["color"]
            })

    # ─── Additional domain‑specific rooms (if any) ───────────
    # You can keep the old domain logic or replace it.
    # For simplicity, we now rely on user selection, but we can add a few extras.
    # We'll add some common rooms based on domain if not already present.
    domain_rooms = []
    if domain == "Residential":
        domain_rooms = [
            {"name": "Grand Living Room", "type": "Living Room", "w": rng.uniform(6, 8), "h": rng.uniform(5, 6), "color": "#2a2a3a"},
            {"name": "Chef's Kitchen Deck", "type": "Kitchen", "w": rng.uniform(4, 5), "h": rng.uniform(3.5, 4.5), "color": "#1a2a1a"},
        ]
    elif domain == "Commercial":
        domain_rooms = [
            {"name": "Co-Working Hub Suite", "type": "Office", "w": rng.uniform(10, 14), "h": rng.uniform(7, 9), "color": "#1a3a4a"},
            {"name": "Executive Dialogue Hall", "type": "Conference", "w": rng.uniform(5, 7), "h": rng.uniform(4, 6), "color": "#2a2a3a"},
        ]
    else:  # Industrial
        domain_rooms = [
            {"name": "Main Production Bay Floor", "type": "Manufacturing", "w": rng.uniform(16, 20), "h": rng.uniform(10, 14), "color": "#2a1a1a"},
            {"name": "Logistics Dispatch Terminal", "type": "Loading Bay", "w": rng.uniform(7, 9), "h": rng.uniform(7, 9), "color": "#3a2a1a"},
        ]
    # Add domain rooms if not already present (by type or name)
    for dr in domain_rooms:
        # Only add if we don't already have a room with that name or type
        if not any(r["name"] == dr["name"] for r in rooms):
            rooms.append(dr)

    # ─── Bathrooms (user may have selected them, but we add extra if baths > 0) ───
    for b in range(baths):
        # Check if we already have a bathroom with that number
        if not any(r["type"] == "Bathroom" and r["name"].endswith(str(b+1)) for r in rooms):
            rooms.append({
                "name": f"Sanitary Bathroom {b+1}",
                "type": "Bathroom",
                "w": rng.uniform(2.5, 3.5),
                "h": rng.uniform(2, 3),
                "color": "#4a2a2a"
            })

    # ─── Ensure minimum number of bedrooms if user selected them ───
    # Not needed – user selection already ensures at least one.

    doors = len(rooms) + floors * rng.randint(1, 3)
    windows = max(4, int(gfa / rng.randint(12, 20)))
    soil_mult = get_soil_multiplier(soil_name)

    return {
        "id": str(uuid.uuid4())[:8].upper(),
        "domain": domain,
        "type": btype,
        "plot_size": plot,
        "floors": floors,
        "floor_area": fa,
        "total_gfa": gfa,
        "rooms": rooms,
        "doors": doors,
        "windows": windows,
        "country": country,
        "soil_name": soil_name,
        "soil_multiplier": soil_mult,
        "structural": {
            "columns": int(cols * floors),
            "beams": int(beams * floors),
            "span": round(span, 2),
            "foundation": foundation,
            "slab_system": slab_system,
            "storey_height": round(storey_height, 2),
            "wall_type": wall_type,
            "concrete_grade": rng.choice(["C25", "C30", "C35", "C40"]),
            "steel_grade": rng.choice(["B500B", "B500C"])
        }
    }