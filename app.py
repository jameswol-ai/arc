# app.py – Full AEC version
from flask import Flask, request, jsonify, render_template
import json, random, uuid, hashlib, requests
from datetime import datetime

app = Flask(__name__)

# ─── SOIL SYSTEM (unchanged) ──────────────────────────────
SOIL_TYPES = { ... }  # same as before

def get_soil_multiplier(soil_name):
    return SOIL_TYPES.get(soil_name, {"multiplier": 1.0})["multiplier"]

# ─── SAI ENGINE – ENHANCED ─────────────────────────────────
ARCH_DOMAINS = {
    "Residential": ["Luxury Villa", "Modern Apartment", "Townhouse Studio"],
    "Commercial": ["Corporate Hub Block", "Boutique Retail Space", "Medical Clinic Center"],
    "Industrial": ["Distribution Depot", "Heavy Machinery Plant Warehouse"],
}

FOUNDATION_TYPES = {
    "Residential": ["Strip Footing", "Raft Foundation", "Pile Foundation"],
    "Commercial": ["Raft Foundation", "Pile Foundation", "Mat Foundation"],
    "Industrial": ["Pile Foundation", "Deep Strip", "Mat Foundation"]
}

SLAB_SYSTEMS = {
    "Residential": ["Flat Slab", "Beam-and-Slab"],
    "Commercial": ["Flat Slab", "Post-Tensioned Slab", "Composite Slab"],
    "Industrial": ["Heavy-duty Slab", "Composite Slab"]
}

def generate_spatial_model(domain, btype, plot_size, floors, baths, country, soil_name, seed=0):
    rng = random.Random(seed)
    plot = max(200, plot_size + rng.randint(-300, 300))
    max_fp = int(plot * rng.uniform(0.5, 0.75))
    fa = min(max_fp, rng.randint(100, int(max_fp * 1.3)))
    gfa = fa * floors

    span = 6.0 if domain == "Residential" else (7.5 if domain == "Commercial" else 12.0)
    span *= rng.uniform(0.85, 1.15)
    cols = max(8, int((fa / (span * 5.0)) * rng.uniform(3, 5)))
    beams = int(cols * rng.uniform(1.5, 2.2))

    # Enhanced structural parameters
    foundation = rng.choice(FOUNDATION_TYPES.get(domain, ["Strip Footing"]))
    slab_system = rng.choice(SLAB_SYSTEMS.get(domain, ["Flat Slab"]))
    storey_height = rng.uniform(3.0, 4.2)  # meters
    wall_type = "Reinforced Concrete" if rng.random() > 0.3 else "Masonry"

    rooms = [ ... ]  # same generation as before

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

def run_eurocode_analysis(d, domain):  # unchanged
    ...

def calculate_ai_scores(...):  # unchanged
    ...

# ─── MATERIAL QUANTITIES & CARBON ──────────────────────────
# Simplified embodied carbon factors (kg CO2e per unit)
CARBON_FACTORS = {
    "concrete": 0.12,      # kg CO2e per kg of concrete (average)
    "steel": 1.85,         # per kg
    "brick": 0.24,         # per unit
    "finish": 5.0          # per m²
}

def compute_materials(d, country):
    gfa = d["total_gfa"]
    floors = d["floors"]
    structural = d["structural"]
    # Simplified quantities per m² of GFA (rough estimates)
    concrete_per_m2 = 0.25  # m³ per m²
    steel_per_m2 = 60       # kg per m²
    brick_per_m2 = 40       # units per m² (for walls)
    finish_per_m2 = 1.0     # m² per m² (floor finishes)

    concrete_vol = concrete_per_m2 * gfa
    steel_weight = steel_per_m2 * gfa
    brick_units = brick_per_m2 * gfa
    finish_area = finish_per_m2 * gfa

    # Carbon
    carbon_concrete = concrete_vol * 2400 * CARBON_FACTORS["concrete"]  # 2400 kg/m³ density
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

# ─── BOQ (enhanced) ──────────────────────────────────────────
def compute_boq(d, country):
    gfa = d["total_gfa"]
    fx = get_fx(country)
    soil_m = d.get("soil_multiplier", 1.0)
    # More detailed items
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
    # Breakdown for frontend
    breakdown = [{"item": item, "quantity": qty, "unit_usd": round(u * fx["multiplier"], 2), "total_usd": round(qty * u * fx["multiplier"], 0)} for item, qty, u in items]
    return total_usd, total_local, fx, breakdown

# ─── FOREX (unchanged) ─────────────────────────────────────
STATIC_FX = {"Kenya":129.49, ...}
BASE_FX = { ... }
def _fetch_live(): ...
def get_fx(country): ...
def get_all_countries(): ...

# ─── RAM AI (unchanged) ────────────────────────────────────
WISDOM = { ... }
TIPS = { ... }
def ram_ai(q, country, domain): ...

# ─── FLASK ROUTES ──────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/forex')
def forex(): ...

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
    weights = data.get('weights', [0.25,0.25,0.25,0.25])

    concepts = []
    for i in range(5):
        d = generate_spatial_model(domain, typology, plot_size + random.randint(-400,400),
                                   max(1, floors + random.randint(-2,2)), max(1, baths + random.randint(-2,2)),
                                   country, soil_name, seed=i)
        d["plan"] = d["rooms"]  # compatibility
        ec = run_eurocode_analysis(d, domain)
        d["eurocode"] = ec
        total_usd, total_local, fx, boq_breakdown = compute_boq(d, country)
        arch, struct, sust, cost, comp = calculate_ai_scores(d, ec, total_usd, "", tuple(weights))
        materials = compute_materials(d, country)
        d["scores"] = {"arch":arch,"struct":struct,"sust":sust,"cost":cost,"composite":comp}
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
            "country": d["country"],
            "scores": d["scores"],
            "total_usd": d["total_usd"],
            "total_local": d["total_local"],
            "eurocode": d["eurocode"],
            "rooms": d["rooms"],
            "structural": d["structural"],
            "materials": d["materials"],
            "boq_breakdown": d["boq_breakdown"],
            "soil_name": d["soil_name"]
        })
    concepts.sort(key=lambda x: x["scores"]["composite"], reverse=True)
    return jsonify(concepts)

@app.route('/api/ram', methods=['POST'])
def ram_endpoint(): ...

if __name__ == '__main__':
    app.run(debug=True)