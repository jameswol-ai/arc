# =========================================================
# Core AEC Engine: spatial model, Eurocode, AI scores
# Fixed weights with Metric Design Intelligence
# Added: Metric-aware space planning, Wind Load Analysis, Seismic Check
# =========================================================

import random, uuid
from .soil import get_soil_multiplier
from .space_planner import generate_metric_plan

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

ROOM_COLORS = {
    "Bedroom": "#2a1a3a", "Bathroom": "#4a2a2a", "Ensuite": "#3a2a3a",
    "Corridor": "#3a3a4a", "Balcony": "#4a4a3a", "Living Room": "#2a2a3a",
    "Kitchen": "#1a2a1a", "Dining Room": "#3a2a2a", "Office": "#2a3a3a",
    "Storage": "#3a3a2a", "Stairs": "#4a4a5a", "Conference": "#2a2a3a",
    "Manufacturing": "#2a1a1a", "Loading Bay": "#3a2a1a",
}


def generate_spatial_model(domain, btype, plot_size, floors, baths, country, soil_name, room_types=None, seed=0):
    """Generate a spatial model using metric-aware planning before AEC analysis."""
    rng = random.Random(seed)
    plot = max(200, plot_size + rng.randint(-300, 300))

    # The planner generates multiple internal layouts and selects the strongest
    # candidate before structural, cost and sustainability analysis.
    selected_types = [r for r in (room_types or []) if r != "Bathroom"]
    plan = generate_metric_plan(
        domain=domain,
        plot_size=plot,
        floors=max(1, floors),
        room_types=selected_types,
        baths=max(0, baths),
        seed=seed,
        candidates=8,
    )

    fa = max(100.0, float(plan.get("floor_area", plot * 0.60)))
    gfa = fa * max(1, floors)
    span = 6.0 if domain == "Residential" else (7.5 if domain == "Commercial" else 12.0)
    span *= rng.uniform(0.85, 1.15)
    cols = max(8, int((fa / (span * 5.0)) * rng.uniform(3, 5)))
    beams = int(cols * rng.uniform(1.5, 2.2))
    foundation = rng.choice(FOUNDATION_TYPES.get(domain, ["Strip Footing"]))
    slab_system = rng.choice(SLAB_SYSTEMS.get(domain, ["Flat Slab"]))
    storey_height = rng.uniform(3.0, 4.2)
    wall_type = "Reinforced Concrete" if rng.random() > 0.3 else "Masonry"

    rooms = []
    for room in plan.get("rooms", []):
        item = dict(room)
        item.pop("area", None)
        item["color"] = ROOM_COLORS.get(item.get("type", ""), "#333333")
        rooms.append(item)

    # Preserve the planning metadata so the UI and downstream engines can
    # distinguish a metric-generated plan from a legacy random layout.
    planning = dict(plan.get("planning", {}))
    planning["selected_candidate"] = plan.get("candidate_index")
    planning["generated_candidates"] = plan.get("generated_candidates", 0)
    planning["metric_planning_score"] = plan.get("metric_planning_score", 0.0)

    doors = len(rooms) + max(1, floors) * rng.randint(1, 3)
    windows = max(4, int(gfa / rng.randint(12, 20)))
    return {
        "id": str(uuid.uuid4())[:8].upper(), "domain": domain, "type": btype,
        "plot_size": plot, "floors": floors, "floor_area": round(fa, 2), "total_gfa": round(gfa, 2),
        "rooms": rooms, "doors": doors, "windows": windows, "country": country,
        "soil_name": soil_name, "soil_multiplier": get_soil_multiplier(soil_name),
        "planning": planning,
        "metric_planning_score": plan.get("metric_planning_score", 0.0),
        "structural": {
            "columns": int(cols * floors), "beams": int(beams * floors), "span": round(span, 2),
            "foundation": foundation, "slab_system": slab_system, "storey_height": round(storey_height, 2),
            "wall_type": wall_type, "concrete_grade": rng.choice(["C25", "C30", "C35", "C40"]),
            "steel_grade": rng.choice(["B500B", "B500C"])
        }
    }


def run_eurocode_analysis(d, domain):
    span = d["structural"]["span"]
    gk = random.uniform(4.5, 6.5)
    qk = 2.0 if domain == "Residential" else (3.5 if domain == "Commercial" else 7.5)
    qk *= random.uniform(0.9, 1.1)
    f_ck, b, d_eff = random.uniform(25, 35), random.uniform(250, 350), random.uniform(400, 500)
    design_load = 1.35 * gk + 1.50 * qk
    w_ed = design_load * random.uniform(4.0, 5.0)
    m_ed = w_ed * span ** 2 / 8
    m_rd = (0.167 * f_ck * b * d_eff ** 2) / 10 ** 6
    return {"design_load": f"{design_load:.2f} kN/m²", "m_ed": f"{m_ed:.1f} kNm", "m_rd": f"{m_rd:.1f} kNm",
            "uls_status": "PASS ✅" if m_rd > m_ed else "FAIL ❌", "f_ck_used": round(f_ck, 1),
            "b_used": round(b), "d_eff_used": round(d_eff)}


def calculate_ai_scores(asset, ec, total_usd, prompt=None, metric_score=None):
    """Return AI discipline scores and a composite score including metric validation."""
    arch = 40 + min(30, asset["floors"] * 4) + min(20, len(asset["rooms"]) * 2.5) + random.randint(-10, 10)
    arch = min(100, arch)
    try:
        m_ed = float(ec["m_ed"].split()[0]); m_rd = float(ec["m_rd"].split()[0])
        struct = 70 + min(30, (m_rd - m_ed) / m_ed * 20)
    except Exception:
        struct = 50
    if ec["uls_status"] != "PASS ✅": struct -= random.randint(20, 40)
    struct = min(100, max(0, int(struct + random.randint(-5, 5))))
    sust = 40 + min(40, int(asset["windows"] * 2.0)) + random.randint(0, 15)
    if prompt and "sustain" in prompt.lower(): sust += 10
    sust = min(100, sust)
    cost = 50 + (30 if total_usd / asset["total_gfa"] < 400 else (20 if total_usd / asset["total_gfa"] < 600 else 5)) + random.randint(-5, 5)
    cost = min(100, int(cost))

    if metric_score is None:
        composite = round((arch + struct + sust + cost) / 4)
    else:
        metric = max(0, min(100, float(metric_score)))
        composite = round(arch * 0.20 + struct * 0.20 + sust * 0.20 + cost * 0.20 + metric * 0.20)
    return arch, struct, sust, cost, composite


def compute_wind_load(d, country):
    wind_speeds = {"Kenya": 25, "Uganda": 22, "Tanzania": 28, "South Sudan": 20, "Rwanda": 18, "Ethiopia": 24}
    v_b = wind_speeds.get(country, 22)
    rho = 1.25
    q_p = 0.5 * rho * v_b ** 2 * 0.8 * 0.85 / 1000
    return {"wind_speed": v_b, "wind_pressure": round(q_p, 2), "base_shear": round(q_p * d["total_gfa"] * 0.8, 0)}


def compute_seismic_check(d, country):
    seismic_zones = {"Kenya": 0.25, "Uganda": 0.20, "Tanzania": 0.30, "South Sudan": 0.15, "Rwanda": 0.35, "Ethiopia": 0.25}
    z = seismic_zones.get(country, 0.20)
    W = d["total_gfa"] * 10
    V = z * 1.0 * 1.2 * W / 4.0
    status = "PASS" if V < 0.1 * W else "FAIL (increase ductility)"
    return {"seismic_zone": z, "base_shear": round(V, 0), "weight": round(W, 0), "status": status}
