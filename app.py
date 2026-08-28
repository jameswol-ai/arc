# =========================================================
# Arc — AEC Intelligence (Standalone Flask App)
# All logic in one file – no external modules
# Deploy on Vercel
# =========================================================

from flask import Flask, request, jsonify, render_template
import json, random, uuid, hashlib, requests
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

app = Flask(__name__)

# ─── 1. UNIT CONVERSION (kept for internal use, but not used in API) ───
M2_TO_FT2, M_TO_FT = 10.7639, 3.28084

def to_display_length(m, unit_system="metric"):
    if unit_system == "imperial":
        return (round(m * M_TO_FT, 1), "ft")
    return (round(m, 1), "m")

def to_display_area(m2, unit_system="metric"):
    if unit_system == "imperial":
        return (round(m2 * M2_TO_FT2, 1), "sq ft")
    return (round(m2, 1), "m²")

def format_length(m, unit_system="metric"):
    val, unit = to_display_length(m, unit_system)
    return f"{val} {unit}"

def format_area(m2, unit_system="metric"):
    val, unit = to_display_area(m2, unit_system)
    return f"{val} {unit}"

# ─── 2. SOIL SYSTEM ──────────────────────────────────────────
SOIL_TYPES = {
    "Nairobi Red Coffee Clay":             {"multiplier": 1.0,  "cat": "Medium", "region": "Kenya"},
    "Kampala Red Lateritic Clay":          {"multiplier": 1.6,  "cat": "Soft",   "region": "Uganda"},
    "Wetland Silts (Kampala)":             {"multiplier": 1.7,  "cat": "Very Soft","region": "Uganda"},
    "Dar Coastal Sand / Coral Limestone":  {"multiplier": 0.85, "cat": "Rock",   "region": "Tanzania"},
    "Juba Black Cotton Soil (Expansive)":  {"multiplier": 1.8,  "cat": "Very Soft","region": "South Sudan"},
    "Kigali Volcanic Andosols":            {"multiplier": 0.7,  "cat": "Rock",   "region": "Rwanda"},
    "Addis Clayey Soils & Volcanic Tuff":  {"multiplier": 1.5,  "cat": "Soft",   "region": "Ethiopia"},
    "Generic Firm Sandy Gravel":           {"multiplier": 1.0,  "cat": "Medium", "region": "All"},
    "Generic Soft Silt / Clay":            {"multiplier": 1.5,  "cat": "Soft",   "region": "All"},
    "Generic Hard Rock / Laterite":        {"multiplier": 0.7,  "cat": "Rock",   "region": "All"},
}

REGION_SOIL_OPTIONS = {
    "Kenya":       ["Nairobi Red Coffee Clay", "Generic Firm Sandy Gravel", "Generic Soft Silt / Clay", "Generic Hard Rock / Laterite"],
    "Uganda":      ["Kampala Red Lateritic Clay", "Wetland Silts (Kampala)", "Generic Firm Sandy Gravel", "Generic Hard Rock / Laterite"],
    "Tanzania":    ["Dar Coastal Sand / Coral Limestone", "Generic Firm Sandy Gravel", "Generic Soft Silt / Clay"],
    "South Sudan": ["Juba Black Cotton Soil (Expansive)", "Generic Firm Sandy Gravel", "Generic Hard Rock / Laterite"],
    "Rwanda":      ["Kigali Volcanic Andosols", "Generic Firm Sandy Gravel", "Generic Soft Silt / Clay"],
    "Ethiopia":    ["Addis Clayey Soils & Volcanic Tuff", "Generic Firm Sandy Gravel", "Generic Hard Rock / Laterite"],
}

def get_soil_multiplier(soil_name):
    return SOIL_TYPES.get(soil_name, {"multiplier": 1.0})["multiplier"]

def get_soil_category(soil_name):
    return SOIL_TYPES.get(soil_name, {"cat": "Medium"})["cat"]

def get_soil_bearing_capacity(soil_name):
    cat = get_soil_category(soil_name)
    if cat == "Rock": return 300
    elif cat == "Medium": return 150
    elif cat == "Soft": return 100
    elif cat == "Very Soft": return 75
    else: return 120

# ─── 3. AEC ENGINE ────────────────────────────────────────────
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

    rooms = [
        {"name": "Central Corridor Gallery", "type": "Corridor", "w": 2.5, "h": 14.0, "color": "#3a3a4a"},
        {"name": "Main Staircase Core", "type": "Stairs", "w": 4.5, "h": 4.0, "color": "#4a4a5a"},
    ]

    if not room_types:
        room_types = []
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
    else:
        domain_rooms = [
            {"name": "Main Production Bay Floor", "type": "Manufacturing", "w": rng.uniform(16, 20), "h": rng.uniform(10, 14), "color": "#2a1a1a"},
            {"name": "Logistics Dispatch Terminal", "type": "Loading Bay", "w": rng.uniform(7, 9), "h": rng.uniform(7, 9), "color": "#3a2a1a"},
        ]
    for dr in domain_rooms:
        if not any(r["name"] == dr["name"] for r in rooms):
            rooms.append(dr)

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

# ─── 4. MATERIALS & CARBON ────────────────────────────────────
CARBON_FACTORS = {"concrete": 0.12, "steel": 1.85, "brick": 0.24, "finish": 5.0}

def compute_materials(d):
    gfa = d["total_gfa"]
    concrete_per_m2 = 0.25
    steel_per_m2 = 60
    brick_per_m2 = 40
    finish_per_m2 = 1.0
    concrete_vol = concrete_per_m2 * gfa
    steel_weight = steel_per_m2 * gfa
    brick_units = brick_per_m2 * gfa
    finish_area = finish_per_m2 * gfa
    carbon_concrete = concrete_vol * 2400 * CARBON_FACTORS["concrete"]
    carbon_steel = steel_weight * CARBON_FACTORS["steel"]
    carbon_brick = brick_units * CARBON_FACTORS["brick"]
    carbon_finish = finish_area * CARBON_FACTORS["finish"]
    total_embodied_carbon = carbon_concrete + carbon_steel + carbon_brick + carbon_finish
    return {
        "concrete_volume": round(concrete_vol, 1),
        "steel_weight": round(steel_weight, 0),
        "brick_units": round(brick_units, 0),
        "finish_area": round(finish_area, 1),
        "embodied_carbon_kg": round(total_embodied_carbon, 0),
        "embodied_carbon_t": round(total_embodied_carbon / 1000, 2)
    }

# ─── 5. STRUCTURAL DESIGN DETAILS ─────────────────────────────
def compute_structural_design(d, ec):
    span = d["structural"]["span"]
    gfa = d["total_gfa"]
    soil_bearing = get_soil_bearing_capacity(d["soil_name"])
    col_width = max(0.3, span / 15)
    col_depth = col_width
    beam_depth = max(0.3, span / 12)
    beam_width = beam_depth / 2
    slab_thickness = max(0.15, span / 30)
    total_load = gfa * 10
    footing_width = max(0.5, total_load / (soil_bearing * 1000))
    fy = 500
    m_ed = float(ec["m_ed"].split()[0])
    d_beam = beam_depth - 0.05
    if d_beam > 0 and m_ed > 0:
        as_beam = (m_ed * 10**6) / (0.87 * fy * 0.9 * d_beam * 1000)
    else:
        as_beam = 0
    as_beam = max(0, as_beam)
    as_col = 0.01 * (col_width * 1000) * (col_depth * 1000)
    as_slab = 0.002 * (slab_thickness * 1000) * 1000
    as_footing = 0.0015 * (footing_width * 1000) * (slab_thickness * 1000)
    def bar_count(area, dia):
        bar_area = np.pi * (dia/2)**2
        return max(1, int(area / bar_area + 0.5))
    return {
        "column_width": round(col_width, 2),
        "column_depth": round(col_depth, 2),
        "beam_width": round(beam_width, 2),
        "beam_depth": round(beam_depth, 2),
        "slab_thickness": round(slab_thickness, 2),
        "footing_width": round(footing_width, 2),
        "footing_depth": 0.3,
        "as_beam": round(as_beam, 0),
        "as_column": round(as_col, 0),
        "as_slab": round(as_slab, 0),
        "as_footing": round(as_footing, 0),
        "beam_bars": bar_count(as_beam, 20),
        "column_bars": bar_count(as_col, 25),
        "slab_bars": bar_count(as_slab, 12),
        "footing_bars": bar_count(as_footing, 16)
    }

# ─── 6. CONSTRUCTION PLANNING ────────────────────────────────
def compute_construction_schedule(d):
    floors = d["floors"]
    gfa = d["total_gfa"]
    tasks = [
        {"id": "A", "name": "Mobilization", "duration": 5, "predecessors": []},
        {"id": "B", "name": "Site Clearance", "duration": 3, "predecessors": ["A"]},
        {"id": "C", "name": "Excavation", "duration": max(3, int(gfa / 200)), "predecessors": ["B"]},
        {"id": "D", "name": "Foundation", "duration": max(4, int(gfa / 150)), "predecessors": ["C"]},
        {"id": "E", "name": "Substructure Columns", "duration": max(3, floors), "predecessors": ["D"]},
        {"id": "F", "name": "Ground Floor Slab", "duration": max(4, int(gfa / 300)), "predecessors": ["E"]},
        {"id": "G1", "name": "Floor 1 Columns", "duration": 3, "predecessors": ["F"]},
        {"id": "G2", "name": "Floor 1 Slab", "duration": 4, "predecessors": ["G1"]},
        {"id": "H1", "name": "Floor 2 Columns", "duration": 3, "predecessors": ["G2"]},
        {"id": "H2", "name": "Floor 2 Slab", "duration": 4, "predecessors": ["H1"]},
        {"id": "I", "name": "Roof", "duration": max(5, int(gfa / 400)), "predecessors": ["H2" if floors >= 2 else "G2"]},
        {"id": "J", "name": "Finishes", "duration": max(6, int(gfa / 200)), "predecessors": ["I"]},
        {"id": "K", "name": "MEP Installation", "duration": max(5, int(gfa / 250)), "predecessors": ["F"]},
        {"id": "L", "name": "External Works", "duration": 5, "predecessors": ["J"]},
        {"id": "M", "name": "Commissioning", "duration": 4, "predecessors": ["J", "K", "L"]},
        {"id": "N", "name": "Handover", "duration": 2, "predecessors": ["M"]},
    ]
    start = datetime.today()
    task_dict = {t["id"]: t for t in tasks}
    visited = set()
    ordered = []
    def visit(n):
        if n in visited: return
        visited.add(n)
        for pred in task_dict[n]["predecessors"]:
            if pred in task_dict:
                visit(pred)
        ordered.append(n)
    for t in tasks:
        if t["id"] not in visited:
            visit(t["id"])
    finish = {}
    schedule = []
    for tid in ordered:
        t = task_dict[tid]
        pred_finish = [finish[p] for p in t["predecessors"] if p in finish]
        if pred_finish:
            start_date = max(pred_finish)
        else:
            start_date = start
        finish_date = start_date + timedelta(days=t["duration"])
        finish[tid] = finish_date
        schedule.append({
            "Task": t["name"],
            "Duration": t["duration"],
            "Start": start_date.isoformat(),
            "Finish": finish_date.isoformat(),
            "Predecessors": ", ".join(t["predecessors"])
        })
    return pd.DataFrame(schedule)

# ─── 7. COST BY TRADE ────────────────────────────────────────
def compute_cost_by_trade(d, country):
    fx = get_fx(country)
    trades = {
        "Excavation": {"items": ["Site Clearance & Excavation"], "labour_pct": 0.4, "equip_pct": 0.3},
        "Concrete": {"items": ["Substructure (Foundations)", "Superstructure Concrete"], "labour_pct": 0.3, "equip_pct": 0.1},
        "Rebar": {"items": ["Steel Reinforcement"], "labour_pct": 0.2, "equip_pct": 0.05},
        "Masonry": {"items": ["Masonry Blocks"], "labour_pct": 0.4, "equip_pct": 0.1},
        "Finishes": {"items": ["Floor Finishes", "Wall Finishes", "Ceiling Finishes"], "labour_pct": 0.5, "equip_pct": 0.05},
        "Doors & Windows": {"items": ["Doors & Windows"], "labour_pct": 0.2, "equip_pct": 0.02},
        "MEP": {"items": ["MEP (Electrical, Plumbing)"], "labour_pct": 0.35, "equip_pct": 0.1},
        "External": {"items": ["External Works"], "labour_pct": 0.4, "equip_pct": 0.2},
    }
    trade_cost = {}
    for trade, info in trades.items():
        total = 0
        for item_name in info["items"]:
            for boq_item in d["boq_breakdown"]:
                if boq_item["Item"] == item_name:
                    total += boq_item["Total USD"]
                    break
        labour = total * info["labour_pct"]
        equip = total * info["equip_pct"]
        trade_cost[trade] = {
            "Material": total - labour - equip,
            "Labour": labour,
            "Equipment": equip,
            "Total": total
        }
    df = pd.DataFrame(trade_cost).T.reset_index().rename(columns={"index": "Trade"})
    df["Total Local"] = df["Total"] * fx["rate"]
    return df.to_dict(orient="records")

# ─── 8. FOREX MODULE ──────────────────────────────────────────
STATIC_FX = {"Kenya":129.49, "Uganda":3665.20, "Tanzania":2625.00, "South Sudan":4626.40, "Rwanda":1330.00, "Ethiopia":125.00}
BASE_FX = {
    "Kenya": ("KES","KSh",1.00,"East Africa"),
    "Uganda": ("UGX","USh",0.95,"East Africa"),
    "Tanzania": ("TZS","TSh",0.98,"East Africa"),
    "South Sudan": ("SSP","SSP",1.35,"East Africa"),
    "Rwanda": ("RWF","FRw",0.85,"Central Africa"),
    "Ethiopia": ("ETB","Br",0.80,"Horn of Africa")
}

def _fetch_live():
    try:
        data = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5).json()["rates"]
        mapping = {"Kenya":"KES","Uganda":"UGX","Tanzania":"TZS","South Sudan":"SSP","Rwanda":"RWF","Ethiopia":"ETB"}
        return {c: data[m[c]] for c in mapping if m[c] in data}
    except:
        return {}

# Cached forex (simple in-memory cache)
_forex_cache = None
def init_fx():
    global _forex_cache
    if _forex_cache is None:
        live = _fetch_live()
        current_rates = {}
        baseline_rates = {}
        currency_info = {}
        for c, (cur, sym, mult, reg) in BASE_FX.items():
            rate = live.get(c, STATIC_FX[c])
            current_rates[c] = rate
            baseline_rates[c] = rate * random.uniform(0.995, 1.005)
            currency_info[c] = {"currency": cur, "symbol": sym, "multiplier": mult, "region": reg}
        _forex_cache = (current_rates, baseline_rates, currency_info)
    return _forex_cache

def get_fx(country):
    _, _, currency_info = init_fx()
    current_rates, _, _ = init_fx()
    return currency_info[country].copy() | {"rate": current_rates[country]}

def get_all_countries():
    return list(STATIC_FX.keys())

def compute_boq(d, country):
    gfa = d["total_gfa"]
    fx = get_fx(country)
    soil_m = d.get("soil_multiplier", 1.0)
    items = [
        ("Site Clearance & Excavation", int(gfa*0.2), 80*soil_m),
        ("Substructure (Foundations)", int(gfa*0.15), 150*soil_m),
        ("Superstructure Concrete", int(gfa*0.35), 210),
        ("Steel Reinforcement", int(gfa*0.35*0.12), 1200),
        ("Masonry Blocks", int(gfa*38), 2.5),
        ("Floor Finishes", int(gfa), 40),
        ("Wall Finishes", int(gfa*2), 25),
        ("Ceiling Finishes", int(gfa), 15),
        ("Doors & Windows", d["doors"] + d["windows"], 350),
        ("MEP (Electrical, Plumbing)", int(gfa*0.1), 500),
        ("External Works", int(gfa*0.05), 200)
    ]
    total_usd = sum(q * (u * fx["multiplier"]) for _, q, u in items)
    total_local = total_usd * fx["rate"]
    breakdown = [{"Item": item, "Qty": qty, "Unit USD": round(u * fx["multiplier"], 2), "Total USD": round(qty * u * fx["multiplier"], 0)} for item, qty, u in items]
    return total_usd, total_local, fx, breakdown

# ─── 9. SOLAR ────────────────────────────────────────────────
def compute_solar_potential(d):
    roof_area = d["total_gfa"]
    irradiation = 1800
    pv_efficiency = 0.18
    capacity_factor = 0.15
    installed_capacity = roof_area * pv_efficiency * 0.1
    annual_energy = installed_capacity * 8760 * capacity_factor
    grid_emission = 0.5
    co2_savings = annual_energy * grid_emission / 1000
    return {
        "roof_area": round(roof_area, 1),
        "installed_capacity": round(installed_capacity, 2),
        "annual_energy": round(annual_energy, 0),
        "co2_savings": round(co2_savings, 2)
    }

# ─── 10. WATER ────────────────────────────────────────────────
def compute_water_harvesting(d):
    roof_area = d["total_gfa"]
    rainfall_map = {
        "Kenya": 600,
        "Uganda": 1200,
        "Tanzania": 900,
        "South Sudan": 800,
        "Rwanda": 1200,
        "Ethiopia": 700
    }
    country = d["country"]
    rainfall_mm = rainfall_map.get(country, 800)
    runoff_coeff = 0.8
    rainfall_m = rainfall_mm / 1000
    harvestable = roof_area * rainfall_m * runoff_coeff
    typical_consumption = 100
    savings_pct = min(100, (harvestable / typical_consumption) * 100)
    return {
        "harvestable_volume": round(harvestable, 1),
        "savings_percentage": round(min(100, savings_pct), 1),
        "rainfall": rainfall_mm
    }

# ─── 11. GREEN RATING ─────────────────────────────────────────
def compute_green_rating(d, ec):
    score = 0
    window_ratio = d["windows"] / d["total_gfa"] if d["total_gfa"] > 0 else 0
    if window_ratio > 0.2:
        score += 10
    elif window_ratio > 0.15:
        score += 7
    else:
        score += 4
    water = compute_water_harvesting(d)
    if water["savings_percentage"] > 50:
        score += 15
    elif water["savings_percentage"] > 30:
        score += 10
    else:
        score += 5
    carbon = d["materials"]["embodied_carbon_t"] / d["total_gfa"] if d["total_gfa"] > 0 else 1
    if carbon < 0.3:
        score += 15
    elif carbon < 0.5:
        score += 10
    else:
        score += 5
    solar = compute_solar_potential(d)
    if solar["installed_capacity"] > 5:
        score += 15
    elif solar["installed_capacity"] > 2:
        score += 10
    else:
        score += 5
    score += 10  # waste management
    if window_ratio > 0.15:
        score += 10
    else:
        score += 5
    if d["structural"]["foundation"] in ["Raft Foundation", "Pile Foundation"]:
        score += 5
    score = min(100, score)
    if score >= 85:
        rating = "Platinum (LEED) / Excellent (BREEAM)"
    elif score >= 70:
        rating = "Gold / Very Good"
    elif score >= 55:
        rating = "Silver / Good"
    else:
        rating = "Certified / Pass"
    return {
        "score": score,
        "rating": rating
    }

# ─── 12. WIND & SEISMIC (simple) ─────────────────────────────
def compute_wind_load(d, country):
    wind_speeds = {
        "Kenya": 25,
        "Uganda": 22,
        "Tanzania": 28,
        "South Sudan": 20,
        "Rwanda": 18,
        "Ethiopia": 24
    }
    v_b = wind_speeds.get(country, 22)
    rho = 1.25
    q_p = 0.5 * rho * (v_b**2) * 0.8 * 0.85 / 1000
    base_shear = q_p * d["total_gfa"] * 0.8
    return {
        "wind_speed": v_b,
        "wind_pressure": round(q_p, 2),
        "base_shear": round(base_shear, 0)
    }

def compute_seismic_check(d, country):
    seismic_zones = {
        "Kenya": 0.25,
        "Uganda": 0.20,
        "Tanzania": 0.30,
        "South Sudan": 0.15,
        "Rwanda": 0.35,
        "Ethiopia": 0.25
    }
    z = seismic_zones.get(country, 0.20)
    W = d["total_gfa"] * 10
    I = 1.0
    S = 1.2
    R = 4.0
    V = z * I * S * W / R
    status = "PASS" if V < 0.1 * W else "FAIL (increase ductility)"
    return {
        "seismic_zone": z,
        "base_shear": round(V, 0),
        "weight": round(W, 0),
        "status": status
    }

# ─── 13. RAM AI ──────────────────────────────────────────────
WISDOM = {
    "soil": ["For soft clay, use raft/pile foundations. Black cotton soil expands when wet—add moisture barrier.",
             "Lateritic soils (Uganda/Rwanda) need erosion protection; strip footings with cover.",
             "Rock sites: pad foundations, but blasting may add 15‑20% cost."],
    "foundation": ["Rift Valley seismic zones: continuous reinforcement, avoid soft storeys.",
                   "Coastal areas (Mombasa, Dar): corrosion‑resistant steel, low w/c ratio."],
    "cost": ["Cement in landlocked countries can be 30% higher; consider alternative binders.",
             "Steel is often imported—hedge with pre‑order agreements."],
    "sustainability": ["Orient long facades to prevailing winds (Indian Ocean monsoon).",
                       "Rainwater harvesting: first‑flush diverters in semi‑arid regions."],
    "default": ["Start with site analysis—soil, climate, materials dictate 70% of design.",
                "Labour affordable but skilled scarce; train and detail simply.",
                "Allow vertical expansion in rapidly urbanising areas."]
}
TIPS = {"Kenya":"Nairobi altitude reduces curing time.", "Uganda":"Termite attack risk on timber.",
        "Tanzania":"Sulphate‑resistant cement for coral limestone.", "South Sudan":"Compaction/soil replacement needed.",
        "Rwanda":"Volcanic soil stable; focus on cooling.", "Ethiopia":"Seismic ductile detailing per Eurocode 8."}

def ram_ai(q, country, domain):
    q = q.lower()
    pool = WISDOM.get("soil" if "soil" in q or "ground" in q else
                      "foundation" if "foundation" in q else
                      "cost" if "cost" in q or "budget" in q else
                      "sustainability" if any(w in q for w in ("sustain","green","eco")) else "default")
    return f"Ram AI: {random.choice(pool)}\n\nTip: {TIPS.get(country, '')}"

# ─── 14. FLASK ROUTES ────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/forex')
def forex():
    rates = {c: get_fx(c)["rate"] for c in get_all_countries()}
    return jsonify(rates)

@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.json
    domain = data.get('domain', 'Residential')
    typology = data.get('typology', 'Luxury Villa')
    plot_size = int(data.get('plot_size', 800))
    floors = int(data.get('floors', 3))
    baths = int(data.get('baths', 2))
    country = data.get('country', 'Kenya')
    soil_name = data.get('soil_name', 'Nairobi Red Coffee Clay')
    room_types = data.get('room_types', ['Bedroom','Bathroom','Living Room','Kitchen'])

    concepts = []
    for i in range(4):
        d = generate_spatial_model(domain, typology, plot_size + random.randint(-400,400),
                                   max(1, floors + random.randint(-2,2)), max(1, baths + random.randint(-2,2)),
                                   country, soil_name, room_types=room_types, seed=i)
        d["plan"] = d["rooms"]
        ec = run_eurocode_analysis(d, domain)
        d["eurocode"] = ec
        total_usd, total_local, fx, boq_breakdown = compute_boq(d, country)
        arch, struct, sust, cost, comp = calculate_ai_scores(d, ec, total_usd, "")
        materials = compute_materials(d)
        d["scores"] = {"arch":arch, "struct":struct, "sust":sust, "cost":cost, "composite":comp}
        d["total_usd"] = total_usd
        d["total_local"] = total_local
        d["fx"] = fx
        d["boq_breakdown"] = boq_breakdown
        d["materials"] = materials

        concepts.append({
            "id": d["id"],
            "type": d["type"],
            "floors": d["floors"],
            "total_gfa": d["total_gfa"],
            "floor_area": d["floor_area"],
            "country": d["country"],
            "soil_name": d["soil_name"],
            "scores": d["scores"],
            "total_usd": d["total_usd"],
            "total_local": d["total_local"],
            "eurocode": d["eurocode"],
            "rooms": d["rooms"],
            "structural": d["structural"],
            "materials": d["materials"],
            "boq_breakdown": d["boq_breakdown"],
            "fx": d["fx"]
        })

    concepts.sort(key=lambda x: x["scores"]["composite"], reverse=True)
    return jsonify(concepts)

@app.route('/api/ram', methods=['POST'])
def ram_endpoint():
    data = request.json
    q = data.get('q', '')
    country = data.get('country', 'Kenya')
    domain = data.get('domain', 'Residential')
    response = ram_ai(q, country, domain)
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True)