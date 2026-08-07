# =========================================================
# Arc — ARCHITECTURAL INTELLECT & EAST AFRICAN FOREX ENGINE
# Flask version – runs on Vercel
# =========================================================

from flask import Flask, request, jsonify, render_template
import json, random, uuid, hashlib, requests
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np, pandas as pd

app = Flask(__name__)

# ═══════════════════════════════════════════════════════════
#  ALL YOUR ORIGINAL FUNCTIONS (copied verbatim from streamlit_app.py)
# ═══════════════════════════════════════════════════════════

# ─── UNIT CONVERSION ──────────────────────────────────────
M2_TO_FT2, M_TO_FT = 10.7639, 3.28084

def to_display_length(m):
    # unit system not used in API; we keep for compatibility
    return (round(m * M_TO_FT, 1), "ft") if False else (round(m, 1), "m")

def to_display_area(m2):
    return (round(m2 * M2_TO_FT2, 1), "sq ft") if False else (round(m2, 1), "m²")

# ─── AUTH & MEMORY (file‑based, note: Vercel doesn't persist files) ──
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
USER_FILE = DATA_DIR / "arc_users.json"
XP_PER_LEVEL = 100

def hash_password(p): return hashlib.sha256((p + "arc_salt_42").encode()).hexdigest()

def load_users():
    if USER_FILE.exists():
        try: return json.load(open(USER_FILE))
        except: return []
    return []

def save_users(users): json.dump(users, open(USER_FILE, "w"), indent=2)

def get_user(u):
    for x in load_users():
        if x["username"] == u: return x
    return None

def create_user(u, p, role="user"):
    if get_user(u): raise ValueError("Username exists")
    users = load_users()
    users.append({"username": u, "password_hash": hash_password(p), "role": role, "level": 1, "xp": 0, "badges": [], "created": datetime.now().isoformat()})
    save_users(users)
    return users[-1]

def authenticate(u, p):
    user = get_user(u)
    return user if user and user["password_hash"] == hash_password(p) else None

def xp_for_level(lvl): return lvl * XP_PER_LEVEL

def add_xp(username, amount):
    user = get_user(username)
    if not user: return False
    user["xp"] += amount
    old = user["level"]
    while user["xp"] >= xp_for_level(user["level"]):
        user["xp"] -= xp_for_level(user["level"]); user["level"] += 1
    if user["level"] > old:
        badge = f"level_{user['level']}"
        if user["level"] % 5 == 0 and badge not in user["badges"]: user["badges"].append(badge)
        update_users = load_users()
        for u in update_users:
            if u["username"] == username: u.update(user); break
        save_users(update_users)
        return True
    return False

def load_memory(username):
    path = DATA_DIR / f"{username}_arc_memory.json"
    if path.exists():
        try: return json.load(open(path, "r", encoding="utf-8"))
        except: pass
    return {"designs": [], "concepts": [], "logs": []}

def save_memory(username, mem): json.dump(mem, open(DATA_DIR / f"{username}_arc_memory.json", "w", encoding="utf-8"), indent=2)

def log_event(username, mem, msg):
    mem["logs"].append({"time": datetime.now().isoformat(), "msg": msg})
    save_memory(username, mem)

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

REGION_SOIL_OPTIONS = {
    "Kenya":       [("Nairobi Red Coffee Clay", "medium"), ("Generic Firm Sandy Gravel", "medium"), ("Generic Soft Silt / Clay", "soft"), ("Generic Hard Rock / Laterite", "rock")],
    "Uganda":      [("Kampala Red Lateritic Clay", "soft"), ("Wetland Silts (Kampala)", "very soft"), ("Generic Firm Sandy Gravel", "medium"), ("Generic Hard Rock / Laterite", "rock")],
    "Tanzania":    [("Dar Coastal Sand / Coral Limestone", "rock"), ("Generic Firm Sandy Gravel", "medium"), ("Generic Soft Silt / Clay", "soft")],
    "South Sudan": [("Juba Black Cotton Soil (Expansive)", "very soft"), ("Generic Firm Sandy Gravel", "medium"), ("Generic Hard Rock / Laterite", "rock")],
    "Rwanda":      [("Kigali Volcanic Andosols", "rock"), ("Generic Firm Sandy Gravel", "medium"), ("Generic Soft Silt / Clay", "soft")],
    "Ethiopia":    [("Addis Clayey Soils & Volcanic Tuff", "soft"), ("Generic Firm Sandy Gravel", "medium"), ("Generic Hard Rock / Laterite", "rock")],
}

def get_soil_multiplier(soil_name):
    return SOIL_TYPES.get(soil_name, {"multiplier": 1.0})["multiplier"]

def get_soil_category(soil_name):
    return SOIL_TYPES.get(soil_name, {"cat": "Medium"})["cat"]

# ─── SAI ENGINE ───────────────────────────────────────────
ARCH_DOMAINS = {
    "Residential": ["Luxury Villa", "Modern Apartment", "Townhouse Studio"],
    "Commercial": ["Corporate Hub Block", "Boutique Retail Space", "Medical Clinic Center"],
    "Industrial": ["Distribution Depot", "Heavy Machinery Plant Warehouse"],
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
        "id": str(uuid.uuid4())[:8].upper(), "domain": domain, "type": btype, "plot_size": plot, "floors": floors,
        "floor_area": fa, "total_gfa": gfa, "rooms": rooms, "doors": doors, "windows": windows,
        "country": country, "soil_name": soil_name, "soil_multiplier": soil_mult,
        "structural": {"columns": int(cols * floors), "beams": int(beams * floors), "span": span}
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

# ─── FOREX ────────────────────────────────────────────────
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

def convert_currency(amount, frm, to):
    # we need current rates; we'll fetch live each time or keep a global cache
    # For simplicity, we'll use STATIC_FX if live unavailable
    rates = _fetch_live()
    if frm == to: return amount
    usd = amount if frm == "USD" else amount / rates.get(frm, STATIC_FX[frm])
    return usd if to == "USD" else usd * rates.get(to, STATIC_FX[to])

def compute_boq(d, country):
    gfa = d["total_gfa"]; fx = get_fx(country); soil_m = d.get("soil_multiplier", 1.0)
    items = [("Substructure Excavation", int(gfa*0.15), 150*soil_m), ("C30 Concrete (m³)", int(gfa*0.35), 210),
             ("Steel Rebar (kg)", int(gfa*0.35*0.12), 1200), ("Blockwork (units)", int(gfa*38), 2.5),
             ("Floor Finishes (m²)", int(gfa), 40), ("Doors", d["doors"], 300), ("Windows", d["windows"], 450)]
    total_usd = sum(q * (u * fx["multiplier"]) for _, q, u in items)
    total_local = total_usd * fx["rate"]
    return total_usd, total_local, fx

# ─── FX HISTORY & FOREST (these functions need Plotly and pandas) ──
# We keep them, but the frontend will use Plotly.js, so we won't call them from the backend.
# However, we may expose data endpoints if needed.

# ─── RAM AI ────────────────────────────────────────────────
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

# ═══════════════════════════════════════════════════════════
#  FLASK ROUTES – serve the frontend and API endpoints
# ═══════════════════════════════════════════════════════════

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/forex')
def forex():
    # Return all country rates
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
    weights = data.get('weights', [0.25, 0.25, 0.25, 0.25])

    concepts = []
    for i in range(5):
        d = generate_spatial_model(domain, typology, plot_size + random.randint(-400,400),
                                   max(1, floors + random.randint(-2,2)), max(1, baths + random.randint(-2,2)),
                                   country, soil_name, seed=i)
        d["plan"] = d["rooms"]  # for compatibility
        ec = run_eurocode_analysis(d, domain)
        d["eurocode"] = ec
        total_usd, total_local, fx = compute_boq(d, country)
        arch, struct, sust, cost, comp = calculate_ai_scores(d, ec, total_usd, "", tuple(weights))
        d["scores"] = {"arch":arch,"struct":struct,"sust":sust,"cost":cost,"composite":comp}
        d["total_usd"] = total_usd
        d["total_local"] = total_local
        d["fx"] = fx
        # Keep only needed fields to reduce payload
        concepts.append({
            "id": d["id"],
            "type": d["type"],
            "floors": d["floors"],
            "total_gfa": d["total_gfa"],
            "country": d["country"],
            "scores": d["scores"],
            "total_usd": d["total_usd"],
            "eurocode": d["eurocode"],
            "rooms_count": len(d["rooms"]),
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

@app.route('/api/convert', methods=['POST'])
def convert():
    data = request.json
    amount = float(data.get('amount', 0))
    frm = data.get('from', 'USD')
    to = data.get('to', 'USD')
    result = convert_currency(amount, frm, to)
    return jsonify({"result": result})

# Optional: health check
@app.route('/api/health')
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(debug=True)