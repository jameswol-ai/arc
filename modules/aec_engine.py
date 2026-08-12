# =========================================================
# Core AEC Engine: spatial model, Eurocode, AI scores
# Fixed weights (no sliders)
# =========================================================

import random, uuid
from .soil import get_soil_multiplier

# ─── Domain definitions ────────────────────────────────────────
ARCH_DOMAINS = {
    "Residential": ["Luxury Villa", "Modern Apartment", "Townhouse Studio"],
    "Commercial": ["Corporate Hub Block", "Boutique Retail Space", "Medical Clinic Center"],
    "Industrial": ["Distribution Depot", "Heavy Machinery Plant Warehouse"],
}

FOUNDATION_TYPES = {
    "Residential": ["Strip Footing", "Raft Foundation", "Pile Foundation"],
    "Commercial": ["Raft Foundation", "Pile Foundation", "Mat Foundation"],
    "Industrial": ["Pile Foundation", "Deep Strip", "Mat Foundation"],
}

SLAB_SYSTEMS = {
    "Residential": ["Flat Slab", "Beam-and-Slab"],
    "Commercial": ["Flat Slab", "Post-Tensioned Slab", "Composite Slab"],
    "Industrial": ["Heavy-duty Slab", "Composite Slab"],
}

# ─── Generate spatial model ───────────────────────────────────
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
    # Add domain rooms if not already present (by name)
    for dr in domain_rooms:
        if not any(r["name"] == dr["name"] for r in rooms):
            rooms.append(dr)

    # ─── Bathrooms (user may have selected them, but we add extra if baths > 0) ───
    for b in range(baths):
        if not any(r["type"] == "Bathroom" and r["name"].endswith(str(b+1)) for r in rooms):
            rooms.append({
                "name": f"Sanitary Bathroom {b+1}",
                "type": "Bathroom",
                "w": rng.uniform(2.5, 3.5),
                "h": rng.uniform(2, 3),
                "color": "#4a2a2a"
            })

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

# ─── Eurocode analysis ──────────────────────────────────────
def run_eurocode_analysis(d, domain):
    span = d["structural"]["span"]
    gk = random.uniform(4.5, 6.5)
    qk = 2.0 if domain == "Residential" else (3.5 if domain == "Commercial" else 7.5)
    qk *= random.uniform(0.9, 1.1)
    f_ck, b, d_eff = random.uniform(25, 35), random.uniform(250, 350), random.uniform(400, 500)
    design_load = 1.35 * gk + 1.50 * qk
    w_ed = design_load * random.uniform(4.0, 5.0)
    m_ed = (w_ed * span**2) / 8
    m_rd = (0.167 * f_ck * b * d_eff**2) / 10**6
    return {
        "design_load": f"{design_load:.2f} kN/m²",
        "m_ed": f"{m_ed:.1f} kNm",
        "m_rd": f"{m_rd:.1f} kNm",
        "uls_status": "PASS ✅" if m_rd > m_ed else "FAIL ❌",
        "f_ck_used": round(f_ck,1),
        "b_used": round(b),
        "d_eff_used": round(d_eff)
    }

# ─── AI scores (fixed weights: 0.25 each) ──────────────────
def calculate_ai_scores(asset, ec, total_usd, prompt=None):
    arch = 40 + min(30, asset['floors']*4) + min(20, len(asset['rooms'])*2.5) + random.randint(-10,10)
    arch = min(100, arch)
    try:
        m_ed = float(ec['m_ed'].split()[0]); m_rd = float(ec['m_rd'].split()[0])
        struct = 70 + min(30, (m_rd - m_ed) / m_ed * 20)
    except:
        struct = 50
    if ec['uls_status'] != "PASS ✅":
        struct -= random.randint(20,40)
    struct = min(100, max(0, int(struct + random.randint(-5,5))))
    sust = 40 + min(40, int(asset['windows']*2.0)) + random.randint(0,15)
    if prompt and 'sustain' in prompt.lower():
        sust += 10
    sust = min(100, sust)
    cost = 50 + (30 if total_usd/asset['total_gfa'] < 400 else (20 if total_usd/asset['total_gfa'] < 600 else 5)) + random.randint(-5,5)
    cost = min(100, int(cost))
    composite = round(arch*0.25 + struct*0.25 + sust*0.25 + cost*0.25)
    return arch, struct, sust, cost, composite


# ─── Add at the end of aec_engine.py ─────────────────────────

# Wind load (simplified Eurocode)
def compute_wind_load(d, country):
    """
    Returns wind pressure (kN/m²) and base shear (kN).
    Uses simplified assumptions.
    """
    # Basic wind speed (m/s) per country (approximate)
    wind_speeds = {
        "Kenya": 25,
        "Uganda": 22,
        "Tanzania": 28,
        "South Sudan": 20,
        "Rwanda": 18,
        "Ethiopia": 24
    }
    v_b = wind_speeds.get(country, 22)  # m/s
    # Terrain category: assume open country (category II)
    # Exposure factor ~ 0.8, shape factor ~ 0.85, etc.
    # Simplified: q_p = 0.5 * rho * v^2 * 0.8 * 0.85
    rho = 1.25  # kg/m³
    q_p = 0.5 * rho * (v_b**2) * 0.8 * 0.85 / 1000  # kN/m²
    # Base shear: q_p * total_gfa * 0.8 (simplified)
    base_shear = q_p * d["total_gfa"] * 0.8
    return {
        "wind_speed": v_b,
        "wind_pressure": round(q_p, 2),
        "base_shear": round(base_shear, 0)
    }

# Seismic check (simplified)
def compute_seismic_check(d, country):
    """
    Returns seismic base shear (kN) and a pass/fail status.
    Uses simplified seismic zone factors.
    """
    # Seismic zone factors (0.1 to 0.4) per country
    seismic_zones = {
        "Kenya": 0.25,
        "Uganda": 0.20,
        "Tanzania": 0.30,
        "South Sudan": 0.15,
        "Rwanda": 0.35,
        "Ethiopia": 0.25
    }
    z = seismic_zones.get(country, 0.20)
    # Importance factor (assume 1.0), soil factor (assume 1.2), damping (assume 5%)
    # Simplified seismic base shear = z * I * S * W / R
    # W = total weight (kN): assume 10 kN/m² per floor
    W = d["total_gfa"] * 10  # kN
    I = 1.0
    S = 1.2  # soil type C
    R = 4.0  # response reduction factor for concrete frame
    V = z * I * S * W / R
    # Check: V should be less than 0.1 * W (simplified)
    status = "PASS" if V < 0.1 * W else "FAIL (increase ductility)"
    return {
        "seismic_zone": z,
        "base_shear": round(V, 0),
        "weight": round(W, 0),
        "status": status
    }