from flask import Flask, request, jsonify, render_template
import json, random, uuid, hashlib, requests
from datetime import datetime

app = Flask(__name__)

# ─── SOIL SYSTEM ──────────────────────────────────────────
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

def get_soil_multiplier(soil_name):
    return SOIL_TYPES.get(soil_name, {"multiplier": 1.0})["multiplier"]

# ─── ENHANCED SAI ENGINE ──────────────────────────────────
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

    foundation = rng.choice(FOUNDATION_TYPES.get(domain, ["Strip Footing"]))
    slab_system = rng.choice(SLAB_SYSTEMS.get(domain, ["Flat Slab"]))
    storey_height = rng.uniform(3.0, 4.2)
    wall_type = "Reinforced Concrete" if rng.random() > 0.3 else "Masonry"

    rooms = [
        {"name": "Central Corridor Gallery", "type": "Corridor", "w": 2.5, "h": 14.0, "color": "#3a3a4a"},
        {"name": "Main Staircase Core", "type": "Stairs", "w": 4.5, "h": 4.0, "color": "#4a4a5a"},
    ]
    if domain == "Residential":
        rooms += [{"name": "Grand Living Room", "type": "Living Room", "w": rng.uniform(6, 8), "h": rng.uniform(5, 6), "color": "#2a2a3a"},
                  {"name": "Chef's Kitchen Deck", "type": "Kitchen", "w": rng.uniform(4, 5), "h": rng.uniform(3.5, 4.5), "color": "#1a2a1a"}]
        for i in range(max(1, int(gfa / rng.randint(60, 90)))):
            rooms.append({"name": f"Master Suite {i+1}", "type": "Bedroom", "w": rng.uniform(4, 5), "h": rng.uniform(3.5, 4.5), "color": "#2a1a3a"})
    elif domain == "Commercial":
        rooms += [{"name": "Co-Working Hub Suite", "type": "Office Space", "w": rng.uniform(10, 14), "h": rng.uniform(7, 9), "color": "#1a3a4a"},
                  {"name": "Executive Dialogue Hall", "type": "Conference", "w": rng.uniform(5, 7), "h": rng.uniform(4, 6), "color": "#2a2a3a"}]
    else:
        rooms += [{"name": "Main Production Bay Floor", "type": "Manufacturing Floor", "w": rng.uniform(16, 20), "h": rng.uniform(10, 14), "color": "#2a1a1a"},
                  {"name": "Logistics Dispatch Terminal", "type": "Loading Bay", "w": rng.uniform(7, 9), "h": rng.uniform(7, 9), "color": "#3a2a1a"}]

    for b in range(baths): rooms.append({"name": f"Sanitary Bathroom {b+1}", "type": "Bathroom", "w": rng.uniform(2.5, 3.5), "h": rng.uniform(2, 3), "color": "#4a2a2a"})
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
    return {"design_load": f"{design_load:.2f} kN/m²", "m_ed": f"{m_ed:.1f} kNm", "m_rd": f"{m_rd:.1f} kNm",
            "uls_status": "PASS ✅" if m_rd > m_ed else "FAIL ❌", "f_ck_used": round(f_ck,1), "b_used": round(b), "d_eff_used": round(d_eff)}

def calculate_ai_scores(asset, ec, total_usd, prompt=None, weights=(0.25,0.25,0.25,0.25)):
    arch = 40 + min(30, asset['floors']*4) + min(20, len(asset['rooms'])*2.5) + random.randint(-10,10)
    arch = min(100, arch)
    try:
        m_ed = float(ec['m_ed'].split()[0]); m_rd = float(ec['m_rd'].split()[0])
        struct = 70 + min(30, (m_rd - m_ed) / m_ed * 20)
    except: struct = 50
    if ec['uls_status'] != "PASS ✅": struct -= random.randint(20,40)
    struct = min(100, max(0, int(struct + random.randint(-5,5))))
    sust = 40 + min(40, int(asset['windows']*2.0)) + random.randint(0,15)
    if prompt and 'sustain' in prompt.lower(): sust += 10
    sust = min(100, sust)
    cost = 50 + (30 if total_usd/asset['total_gfa'] < 400 else (20 if total_usd/asset['total_gfa'] < 600 else 5)) + random.randint(-5,5)
    cost = min(100, int(cost))
    w = weights
    composite = round(arch*w[0] + struct*w[1] + sust*w[2] + cost*w[3])
    return arch, struct, sust, cost, composite

# ─── MATERIAL QUANTITIES & CARBON ────────────────────────
CARBON_FACTORS = {"concrete": 0.12, "steel": 1.85, "brick": 0.24, "finish": 5.0}

def compute_materials(d, country):
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

# ─── BOQ ──────────────────────────────────────────────────
STATIC_FX = {"Kenya":129.49, "Uganda":3665.20, "Tanzania":2625.00, "South Sudan":4626.40, "Rwanda":1330.00, "Ethiopia":125.00}
BASE_FX = {
    "Kenya": ("KES","KSh",1.00,"East Africa"), "Uganda": ("UGX","USh",0.95,"East Africa"),
    "Tanzania": ("TZS","TSh",0.98,"East Africa"), "South Sudan": ("SSP","SSP",1.35,"East Africa"),
    "Rwanda": ("RWF","FRw",0.85,"Central Africa"), "Ethiopia": ("ETB","Br",0.80,"Horn of Africa")
}

def _fetch_live():
    try:
        data = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5).json()["rates"]
        mapping = {"Kenya":"KES","Uganda":"UGX","Tanzania":"TZS","South Sudan":"SSP","Rwanda":"RWF","Ethiopia":"ETB"}
        return {c: data[m[c]] for c in mapping if m[c] in data}
    except: return {}

def get_fx(country):
    live = _fetch_live()
    rate = live.get(country, STATIC_FX[country])
    cur, sym, mult, reg = BASE_FX[country]
    return {"currency": cur, "symbol": sym, "rate": rate, "multiplier": mult, "region": reg}

def get_all_countries(): return list(STATIC_FX.keys())

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
    breakdown = [{"item": item, "quantity": qty, "unit_usd": round(u * fx["multiplier"], 2), "total_usd": round(qty * u * fx["multiplier"], 0)} for item, qty, u in items]
    return total_usd, total_local, fx, breakdown

# ─── RAM AI ──────────────────────────────────────────────
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
    return f"**Ram AI:** {random.choice(pool)}\n\n📌 *{country}*: {TIPS.get(country, '')}"

# ─── FLASK ROUTES ─────────────────────────────────────────
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
    weights = data.get('weights', [0.25,0.25,0.25,0.25])

    concepts = []
    for i in range(5):
        d = generate_spatial_model(domain, typology, plot_size + random.randint(-400,400),
                                   max(1, floors + random.randint(-2,2)), max(1, baths + random.randint(-2,2)),
                                   country, soil_name, seed=i)
        d["plan"] = d["rooms"]
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
def ram_endpoint():
    data = request.json
    q = data.get('q', '')
    country = data.get('country', 'Kenya')
    domain = data.get('domain', 'Residential')
    response = ram_ai(q, country, domain)
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True)