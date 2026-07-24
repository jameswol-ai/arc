# =========================================================
# Arc — ARCHITECTURAL INTELLECT & EAST AFRICAN FOREX ENGINE
# streamlit_app.py – Black & Grey Theme, No Logos/Images
# Improved Soil Selection & Error Fixes
# =========================================================

import streamlit as st
import json, random, uuid, hashlib, requests
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np, pandas as pd

# ════════════════  UNIT CONVERSION  ════════════════
M2_TO_FT2, M_TO_FT = 10.7639, 3.28084

def to_display_length(m):
    return (round(m * M_TO_FT, 1), "ft") if st.session_state.get("unit_system") == "imperial" else (round(m, 1), "m")

def to_display_area(m2):
    return (round(m2 * M2_TO_FT2, 1), "sq ft") if st.session_state.get("unit_system") == "imperial" else (round(m2, 1), "m²")

# ════════════════  AUTH & MEMORY  ════════════════
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

# ════════════════  ENHANCED SOIL SYSTEM  ════════════════
# Common East African soil types with multipliers
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

# Country → list of (soil_name, desc) for the dropdown
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

# ════════════════  SAI ENGINE  ════════════════
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

# ════════════════  FOREX MODULE  ════════════════
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

@st.cache_resource
def init_fx():
    live = _fetch_live()
    current_rates = {}
    baseline_rates = {}
    currency_info = {}
    for c, (cur, sym, mult, reg) in BASE_FX.items():
        rate = live.get(c, STATIC_FX[c])
        current_rates[c] = rate
        baseline_rates[c] = rate * random.uniform(0.995, 1.005)
        currency_info[c] = {"currency": cur, "symbol": sym, "multiplier": mult, "region": reg}
    return current_rates, baseline_rates, currency_info

_CURRENT_RATES, _BASELINE_RATES, _CURRENCY_INFO = init_fx()

def get_fx(country): return _CURRENCY_INFO[country].copy() | {"rate": _CURRENT_RATES[country]}

def get_all_countries(): return list(STATIC_FX.keys())

def convert_currency(amount, frm, to):
    if frm == to: return amount
    usd = amount if frm == "USD" else amount / _CURRENT_RATES[frm]
    return usd if to == "USD" else usd * _CURRENT_RATES[to]

def compute_boq(d, country):
    gfa = d["total_gfa"]; fx = get_fx(country); soil_m = d.get("soil_multiplier", 1.0)
    items = [("Substructure Excavation", int(gfa*0.15), 150*soil_m), ("C30 Concrete (m³)", int(gfa*0.35), 210),
             ("Steel Rebar (kg)", int(gfa*0.35*0.12), 1200), ("Blockwork (units)", int(gfa*38), 2.5),
             ("Floor Finishes (m²)", int(gfa), 40), ("Doors", d["doors"], 300), ("Windows", d["windows"], 450)]
    total_usd = sum(q * (u * fx["multiplier"]) for _, q, u in items)
    total_local = total_usd * fx["rate"]
    return total_usd, total_local, fx

# ════════════════  FX HISTORY & FOREST  ════════════════
@st.cache_data(ttl=3600)
def fetch_hist(start, end):
    try:
        url = f"https://api.exchangerate.host/timeseries?start_date={start}&end_date={end}&base=USD&symbols=KES,UGX,TZS,SSP,RWF,ETB"
        data = requests.get(url, timeout=10).json()["rates"]
        df = pd.DataFrame({c: [data[d].get(c) for d in sorted(data)] for c in ["KES","UGX","TZS","SSP","RWF","ETB"]},
                          index=pd.to_datetime(sorted(data.keys()))).ffill()
        return df
    except: return None

def plot_hist(df):
    fig = go.Figure()
    colors = {"KES":"#888","UGX":"#aaa","TZS":"#666","SSP":"#999","RWF":"#777","ETB":"#555"}
    for c in df.columns: fig.add_trace(go.Scatter(x=df.index, y=df[c], mode='lines', name=c, line=dict(color=colors.get(c,'#94a3b8'))))
    fig.update_layout(title="East African FX Rates – 60 days", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#aaaaaa', margin=dict(l=20,r=20,t=40,b=20))
    return fig

def forest(base, days=7, n_paths=100, vol=0.008):
    rng = np.random.default_rng(42)
    p = [rng.normal(0, vol, days) for _ in range(n_paths)]
    sim_paths = np.cumprod(1 + np.array(p), axis=1) * base
    fig = go.Figure()
    x = list(range(1, days+1))
    band_colors = [
        (95, "rgba(70, 130, 200, 0.08)"),
        (80, "rgba(70, 130, 200, 0.15)"),
        (50, "rgba(70, 130, 200, 0.25)")
    ]
    for perc, fill_color in band_colors:
        lower = np.percentile(sim_paths, (100-perc)/2, axis=0)
        upper = np.percentile(sim_paths, 100 - (100-perc)/2, axis=0)
        fig.add_trace(go.Scatter(x=x, y=upper, mode='lines', line=dict(width=0), showlegend=False))
        fig.add_trace(go.Scatter(x=x, y=lower, mode='lines', fill='tonexty', fillcolor=fill_color,
                                 line=dict(width=0), name=f'{perc}% confidence'))
    median = np.median(sim_paths, axis=0)
    fig.add_trace(go.Scatter(x=x, y=median, mode='lines+markers', name='Median',
                             line=dict(color='#7bb8ff', width=2.5),
                             marker=dict(color='#b0d0ff', size=6)))
    fig.update_layout(title="Weekly Forecast", plot_bgcolor='rgba(0,0,0,0)',
                      paper_bgcolor='rgba(0,0,0,0)', font_color='#aaaaaa',
                      margin=dict(l=20,r=20,t=40,b=20), legend=dict(orientation="h", yanchor="bottom", y=1.02))
    return fig

# ════════════════  RAM AI  ════════════════
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

# ════════════════  RENDERERS  ════════════════
def render_floorplan(plan, span=6.0):
    corridor = next((r for r in plan if r["type"]=="Corridor"), plan[0])
    stairs = next((r for r in plan if r["type"]=="Stairs"), None)
    others = [r for r in plan if r not in (corridor, stairs)]
    unit = "ft" if st.session_state.get("unit_system")=="imperial" else "m"
    fig = go.Figure()
    def add_room(x0, y0, x1, y1, color, name, w_m, d_m):
        w_d, _ = to_display_length(w_m); d_d, _ = to_display_length(d_m)
        fig.add_shape(type="rect", x0=x0, y0=y0, x1=x1, y1=y1, fillcolor=color, line=dict(color="#555", width=2), opacity=0.7)
        fig.add_annotation(x=(x0+x1)/2, y=(y0+y1)/2, text=f"<b>{name}</b><br>{w_d}×{d_d} {unit}", showarrow=False, font=dict(size=10, color="#cccccc"), bgcolor="rgba(0,0,0,0.7)")
    cl, cw = corridor["h"], corridor["w"]
    max_x = cl + 5; max_y = cw + sum(r["h"] for r in others) + 5
    for x in np.arange(0, max_x + span, span): fig.add_shape(type="line", x0=x, y0=-max_y, x1=x, y1=max_y, line=dict(color="rgba(100,100,100,0.2)", width=1), layer="below")
    for y in np.arange(-max_y, max_y, span): fig.add_shape(type="line", x0=0, y0=y, x1=max_x, y1=y, line=dict(color="rgba(100,100,100,0.2)", width=1), layer="below")
    add_room(0, -cw/2, cl, cw/2, corridor["color"], corridor["name"], corridor["w"], corridor["h"])
    cx, side = 1.5, 1
    for room in others:
        rw, rd = room["w"], room["h"]
        if cx + rw > cl: cx, side = 1.5, -side
        y0 = cw/2 + 0.5 if side==1 else -cw/2 - 0.5 - rd
        y1 = y0 + rd
        add_room(cx, y0, cx + rw, y1, room["color"], room["name"], rw, rd)
        door_x, door_y = cx + rw/2, cw/2 if side==1 else -cw/2
        fig.add_shape(type="path", path=f"M {door_x-0.3},{door_y} Q {door_x-0.3},{door_y+(0.6 if side==1 else -0.6)} {door_x+0.3},{door_y+(0.6 if side==1 else -0.6)} Q {door_x+0.3},{door_y} {door_x-0.3},{door_y}", line=dict(color="#888", width=2), fillcolor="rgba(100,100,100,0.2)")
        fig.add_annotation(x=(door_x), y=(y0+y1)/2, ax=door_x, ay=door_y, xref="x", yref="y", axref="x", ayref="y", text="", showarrow=True, arrowhead=3, arrowcolor="#888")
        cx += rw + 0.8; side *= -1
    if stairs:
        sx = cl + 0.5
        add_room(sx, -cw/2, sx+stairs["w"], cw/2, stairs["color"], stairs["name"], stairs["w"], stairs["h"])
        fig.add_annotation(x=sx+stairs["w"]/2, y=0, ax=cl-0.5, ay=0, xref="x", yref="y", axref="x", ayref="y", text="", showarrow=True, arrowhead=3, arrowcolor="#888")
    fig.add_annotation(x=0.5, y=0, ax=-1, ay=0, xref="x", yref="y", axref="x", ayref="y", text="<b>ENTRANCE</b>", showarrow=True, arrowhead=3, arrowcolor="#888", font=dict(color="#888"))
    fig.update_layout(title="🗺️ 2D Floor Plan", xaxis=dict(visible=False), yaxis=dict(visible=False, scaleanchor="x", scaleratio=1),
                      plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=20,r=20,t=40,b=20), showlegend=False, width=800, height=500)
    return fig

def render_3d(plan, floors=1, span=6.0):
    traces = []
    min_x = min_y = float('inf'); max_x = max_y = -float('inf')
    for i, r in enumerate(plan):
        xc = (i%3)*12; yc = (i//3)*10
        min_x = min(min_x, xc - r["w"]/2); max_x = max(max_x, xc + r["w"]/2)
        min_y = min(min_y, yc - r["h"]/2); max_y = max(max_y, yc + r["h"]/2)
    gs = span*2
    for x in range(int(min_x/gs)*int(gs), int(max_x/gs+1)*int(gs)+1, int(gs)):
        traces.append(go.Scatter3d(x=[x,x], y=[min_y, max_y], z=[0,0], mode='lines', line=dict(color='#333', width=1), showlegend=False))
    for y in range(int(min_y/gs)*int(gs), int(max_y/gs+1)*int(gs)+1, int(gs)):
        traces.append(go.Scatter3d(x=[min_x, max_x], y=[y,y], z=[0,0], mode='lines', line=dict(color='#333', width=1), showlegend=False))
    for i, r in enumerate(plan):
        xc = (i%3)*12; yc = (i//3)*10
        w, d, c = r["w"], r["h"], r["color"]
        for f in range(floors):
            zb = f*3; zt = zb+2.7
            xb = [xc-w/2, xc+w/2, xc+w/2, xc-w/2, xc-w/2]; yb = [yc-d/2, yc-d/2, yc+d/2, yc+d/2, yc-d/2]
            traces.append(go.Scatter3d(x=xb, y=yb, z=[zb]*5, mode='lines', line=dict(color=c, width=2), showlegend=False))
            traces.append(go.Scatter3d(x=xb, y=yb, z=[zt]*5, mode='lines', line=dict(color=c, width=2), showlegend=False))
            for cx, cy in [(xc-w/2,yc-d/2),(xc+w/2,yc-d/2),(xc+w/2,yc+d/2),(xc-w/2,yc+d/2)]:
                traces.append(go.Scatter3d(x=[cx,cx], y=[cy,cy], z=[zb,zt], mode='lines', line=dict(color=c, width=2), showlegend=False))
    for gx in range(int(min_x/gs)*int(gs), int(max_x/gs+1)*int(gs)+1, int(gs)):
        for gy in range(int(min_y/gs)*int(gs), int(max_y/gs+1)*int(gs)+1, int(gs)):
            traces.append(go.Scatter3d(x=[gx,gx], y=[gy,gy], z=[0, floors*3], mode='lines', line=dict(color='#555', width=2, dash='dot'), showlegend=False))
    fig = go.Figure(data=traces)
    fig.update_layout(scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False), bgcolor='#0a0a0a'),
                      paper_bgcolor='#0a0a0a', margin=dict(l=0,r=0,b=0,t=20), showlegend=False, title="3D Massing", title_font=dict(color='#aaaaaa', size=14))
    return fig

def render_isometric(plan, span=6.0):
    w_, h_ = 800, 380; unit = "ft" if st.session_state.get("unit_system")=="imperial" else "m"
    js = f"ctx.strokeStyle='rgba(100,100,100,0.1)';ctx.lineWidth=1;const step={span*2};for(let x=0;x<{w_};x+=step){{ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,{h_});ctx.stroke();}}for(let y=0;y<{h_};y+=step){{ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo({w_},y);ctx.stroke();}}"
    for i, r in enumerate(plan):
        ox = (i%3)*170+100; oy = (i//3)*110+130
        rw = min(115, int(r["w"]*14)); rh = min(95, int(r["h"]*14)); c = r["color"]
        wd, _ = to_display_length(r["w"]); hd, _ = to_display_length(r["h"])
        js += f"ctx.fillStyle='{c}';ctx.beginPath();ctx.moveTo({ox},{oy});ctx.lineTo({ox+rw},{oy-rh/2});ctx.lineTo({ox+rw+rw},{oy});ctx.lineTo({ox+rw},{oy+rh/2});ctx.closePath();ctx.fill();ctx.strokeStyle='rgba(200,200,200,0.3)';ctx.stroke();ctx.fillStyle='rgba(200,200,200,0.06)';ctx.beginPath();ctx.moveTo({ox},{oy});ctx.lineTo({ox},{oy-40});ctx.lineTo({ox+rw},{oy+rh/2-40});ctx.lineTo({ox+rw},{oy+rh/2});ctx.closePath();ctx.fill();ctx.stroke();ctx.fillStyle='#ccc';ctx.font='bold 11px Space Grotesk';ctx.fillText('{r["name"]} ({wd}×{hd} {unit})',{ox+15},{oy-2});"
    return f"<canvas width='{w_}' height='{h_}' style='max-width:100%;background:#0a0a0a;'></canvas><script>const c=document.querySelector('canvas');const ctx=c.getContext('2d');{js}</script>"

def boq_table(asset):
    gfa = asset["total_gfa"]; fx = asset["fx"]; sm = asset.get("soil_multiplier", 1.0)
    items = [("Substructure", int(gfa*0.15), 150*sm), ("C30 Concrete", int(gfa*0.35), 210), ("Steel Rebar", int(gfa*0.35*0.12), 1200),
             ("Blockwork", int(gfa*38), 2.5), ("Floor Finishes", int(gfa), 40), ("Doors", asset["doors"], 300), ("Windows", asset["windows"], 450)]
    rows = []
    for desc, qty, unit_usd in items:
        adj = unit_usd * fx["multiplier"]
        rows.append({"Item": desc, "Qty": qty, "Unit USD": f"${adj:,.2f}", "Total USD": f"${qty*adj:,.0f}", f"Total {fx['currency']}": f"{fx['symbol']} {qty*adj*fx['rate']:,.0f}"})
    return pd.DataFrame(rows)

def describe_concept(asset):
    gfa_m, gfa_ft = asset['total_gfa'], round(asset['total_gfa']*M2_TO_FT2,1)
    return f"{asset['type']}, {asset['floors']}‑storey, {len(asset['plan'])} rooms, {asset['country']}. Soil: {asset.get('soil_name','N/A')}. GFA: {gfa_m} m² ({gfa_ft} sq ft)"

def gantt_chart(asset):
    gfa = asset["total_gfa"]; fl = asset["floors"]; s = datetime.today()
    tasks = [("Mobilization",5),("Substructure",int(gfa*0.15))] + [(f"Floor {i+1}",20) for i in range(fl)] + [("Roofing",12),("Finishes",int(gfa*0.02)),("Commissioning",14),("Handover",3)]
    df = pd.DataFrame(tasks, columns=["Task","Duration"])
    ends = [s]; [ends.append(ends[-1] + timedelta(days=d)) for d in df["Duration"]]
    df["Start"] = ends[:-1]; df["Finish"] = ends[1:]
    fig = px.timeline(df, x_start="Start", x_end="Finish", y="Task", title="📅 Gantt Chart")
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#aaaaaa'))
    return fig

# ════════════════  UI  ════════════════
st.set_page_config(page_title="Arc – Sai Engine", page_icon="◈", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html,body,.stApp{background:#0a0a0a;color:#cccccc;font-family:'Inter',sans-serif}
.glass-panel{background:#111111;border:1px solid #333333;border-radius:18px;padding:20px}
.stButton>button{background:#333333;color:#ffffff;border:none;border-radius:10px;font-weight:600;padding:8px 20px;transition:all .2s;box-shadow:0 2px 8px rgba(0,0,0,0.5)}
.stButton>button:hover{background:#444444;box-shadow:0 4px 12px rgba(0,0,0,0.8)}
[data-testid="stSidebar"]{background:#0a0a0a;border-right:1px solid #222}
.stTextInput>div>div>input,.stNumberInput input,.stSelectbox>div>div,.stTextArea textarea{background:transparent!important;border:1px solid #333!important;border-radius:8px;color:#cccccc!important}
.metric-bar-bg{background:#222;border-radius:5px;height:6px}
.metric-bar-fg{border-radius:5px;background:#888;height:6px}
.stMetric .stMetricLabel{color:#aaaaaa!important}
.stMetric .stMetricValue{color:#cccccc!important}
div[data-testid="stMetricDelta"]{color:#aaaaaa!important}
</style>
""", unsafe_allow_html=True)

# Session init
if "logged_in" not in st.session_state:
    st.session_state.logged_in, st.session_state.username, st.session_state.user_data = False, None, None
    st.session_state.memory = {"designs": [], "concepts": [], "logs": []}
    st.session_state.generated_concepts, st.session_state.active_design = [], None
    st.session_state.unit_system, st.session_state.ram_history = "metric", []
    st.session_state.selected_soil_name = "Nairobi Red Coffee Clay"   # default

if not load_users(): create_user("admin", "admin123")

# ════════════════  LOGIN  ════════════════
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<div style='text-align:center;font-size:2rem;font-weight:300;color:#aaaaaa;'>◈ Arc</div>", unsafe_allow_html=True)
        with st.form("auth"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            c1, c2 = st.columns(2)
            with c1: login_btn = st.form_submit_button("Login")
            with c2: reg_btn = st.form_submit_button("Sign up")
            if login_btn:
                user = authenticate(username, password)
                if user:
                    st.session_state.logged_in, st.session_state.username, st.session_state.user_data = True, username, user
                    st.session_state.memory = load_memory(username)
                    st.rerun()
                else: st.error("Invalid credentials.")
            if reg_btn:
                if not username or not password: st.error("Fill all fields.")
                else:
                    try: create_user(username, password); st.success("Account created! Log in now.")
                    except ValueError as e: st.error(str(e))
    st.stop()

# ════════════════  SIDEBAR  ════════════════
username = st.session_state.username; user = st.session_state.user_data; mem = st.session_state.memory

with st.sidebar:
    st.markdown("<div style='text-align:center;font-size:1.4rem;font-weight:300;color:#aaaaaa;'>◈ Arc</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align:center;font-size:0.9rem;color:#888;'>{username} · Lvl {user['level']}</div>", unsafe_allow_html=True)
    lvl, xp = user["level"], user["xp"]; needed = xp_for_level(lvl); prog = xp/needed if needed else 1
    st.markdown(f"<div style='display:flex;align-items:center;gap:6px;margin:10px 0'><span style='font-size:10px;color:#888;'>LVL {lvl}</span><div style='flex:1;height:5px;background:#222;border-radius:2px'><div style='width:{prog*100}%;height:100%;background:#888;border-radius:2px'></div></div><span style='font-size:9px;color:#666;'>{xp}/{needed} XP</span></div>", unsafe_allow_html=True)
    unit = st.selectbox("📏 Unit System", ["Metric (m, m²)", "Imperial (ft, sq ft)"])
    st.session_state.unit_system = "metric" if "Metric" in unit else "imperial"
    nav = st.radio("Navigate", ["Dashboard", "Concepts", "Ram AI"])
    st.markdown("---")

    with st.expander("📐 Arc Configuration", expanded=True):
        st.markdown("**Trade Region · East African Countries**")
        country = st.selectbox("Country", list(STATIC_FX.keys()))
        domain = st.selectbox("Domain", list(ARCH_DOMAINS.keys()))
        typology = st.selectbox("Typology", ARCH_DOMAINS[domain])
        plot = st.slider("Plot Area (m²)", 200, 5000, 800, step=50)
        if st.session_state.unit_system == "imperial": st.caption(f"= {round(plot*M2_TO_FT2,0)} sq ft")
        floors = st.slider("Floors", 1, 12, 3)
        baths = st.slider("Bathrooms", 1, 10, 2)

        # Enhanced soil selection
        soil_options = REGION_SOIL_OPTIONS.get(country, [("Generic Firm Sandy Gravel", "medium")])
        soil_names = [opt[0] for opt in soil_options]
        default_idx = 0   # first in list
        # persist selection across reruns
        prev_soil = st.session_state.selected_soil_name
        if prev_soil in soil_names:
            default_idx = soil_names.index(prev_soil)
        selected_soil = st.selectbox("🌱 Soil Condition", soil_names, index=default_idx,
                                      format_func=lambda x: f"{x} ({get_soil_category(x)}, {get_soil_multiplier(x)}x)")
        st.session_state.selected_soil_name = selected_soil

    with st.expander("⚖️ AI Weights", expanded=False):
        w_arch = st.slider("Architecture", 0.0, 1.0, 0.25, 0.05)
        w_struct = st.slider("Structural", 0.0, 1.0, 0.25, 0.05)
        w_sust = st.slider("Sustainability", 0.0, 1.0, 0.25, 0.05)
        w_cost = st.slider("Cost", 0.0, 1.0, 0.25, 0.05)
        total_w = w_arch+w_struct+w_sust+w_cost
        if total_w>0: w_arch/=total_w; w_struct/=total_w; w_sust/=total_w; w_cost/=total_w
        weights = (w_arch, w_struct, w_sust, w_cost)
        st.caption(f"Norm: arch {w_arch:.2f} struct {w_struct:.2f} sust {w_sust:.2f} cost {w_cost:.2f}")

    if st.button("✨ Generate Concepts", use_container_width=True):
        with st.spinner("Synthesizing 5 concepts..."):
            concepts = []
            soil_name = st.session_state.selected_soil_name
            for i in range(5):
                d = generate_spatial_model(domain, typology, plot+random.randint(-400,400),
                                           max(1, floors+random.randint(-2,2)), max(1, baths+random.randint(-2,2)),
                                           country, soil_name, seed=i)
                d["plan"] = d["rooms"]
                ec = run_eurocode_analysis(d, domain)
                d["eurocode"] = ec
                total_usd, total_local, fx = compute_boq(d, country)
                arch, struct, sust, cost, comp = calculate_ai_scores(d, ec, total_usd, "", weights)
                d["scores"] = {"arch":arch,"struct":struct,"sust":sust,"cost":cost,"composite":comp}
                d["total_usd"], d["total_local"], d["fx"] = total_usd, total_local, fx
                concepts.append(d)
            concepts.sort(key=lambda x: x["scores"]["composite"], reverse=True)
            st.session_state.generated_concepts = concepts
            st.session_state.active_design = concepts[0]
            log_event(username, mem, f"Generated 5 concepts. Alpha: {concepts[0]['id']}")
            leveled_up = add_xp(username, 20)
            st.session_state.user_data = get_user(username)
            if leveled_up: st.balloons()
            st.rerun()

    with st.expander("💱 Forex Converter", expanded=False):
        if st.button("🔄 Refresh Rates", use_container_width=True): init_fx.clear(); init_fx(); st.rerun()
        curr_list = ["USD"] + list(STATIC_FX.keys())
        from_cur = st.selectbox("From", curr_list, key="conv_from")
        to_cur = st.selectbox("To", curr_list, key="conv_to")
        amount = st.number_input("Amount", value=1000.0, step=100.0)
        res = convert_currency(amount, from_cur, to_cur)
        sym_from = "$" if from_cur=="USD" else get_fx(from_cur)["symbol"]
        sym_to = "$" if to_cur=="USD" else get_fx(to_cur)["symbol"]
        st.metric(f"{sym_from} {amount:,.2f}", f"{sym_to} {res:,.2f}")

    if st.button("🚪 Logout", use_container_width=True): save_memory(username, mem); st.session_state.logged_in = False; st.rerun()

# ════════════════  MAIN AREA  ════════════════
if nav == "Dashboard":
    st.markdown("<div class='glass-panel' style='text-align:center;margin-bottom:24px;'><h2 style='margin:0;color:#aaaaaa;'>Welcome back, Architect 👋</h2><p style='color:#888;'>Create. Evolve. Perfect.</p></div>", unsafe_allow_html=True)
    st.markdown("### 💹 Live East African FX Rates")
    cols = st.columns(6)
    for i, c in enumerate(get_all_countries()):
        data = get_fx(c); rate = data["rate"]; base = _BASELINE_RATES[c]
        change = ((rate - base) / base) * 100
        color = "#888" if change>=0 else "#555"
        with cols[i]:
            st.markdown(f"<div class='glass-panel' style='padding:12px 4px;text-align:center;'><div style='font-size:0.75rem;color:#888;'>{c}</div><div style='font-size:1.3rem;font-weight:600;color:#ccc;'>{data['symbol']} {rate:.2f}</div><div style='font-size:0.7rem;color:{color};'>{'+' if change>=0 else ''}{change:.2f}%</div></div>", unsafe_allow_html=True)
    st.markdown("---")
    with st.expander("📈 East African FX History (60 days)", expanded=True):
        end_date = datetime.today(); start_date = end_date - timedelta(days=60)
        df_hist = fetch_hist(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        if df_hist is not None and not df_hist.empty:
            st.plotly_chart(plot_hist(df_hist), use_container_width=True)
        else:
            st.info("Live data unavailable – showing simulated trends.")
            base_rates = {c: _CURRENT_RATES[c] for c in get_all_countries()}
            sim = {}
            dates = [start_date + timedelta(days=i) for i in range(61)]
            for c, r in base_rates.items():
                rng = np.random.default_rng(42)
                steps = rng.normal(0, 0.005, len(dates)-1)
                vals = [r]
                for s in steps:
                    vals.append(vals[-1] * (1 + s))
                sim[c] = vals[1:]
            df_sim = pd.DataFrame(sim, index=dates[1:])
            st.plotly_chart(plot_hist(df_sim), use_container_width=True)
    st.markdown("---")
    st.markdown("### 🌳 Forex Forest – Weekly Forecast")
    st.caption("Monte Carlo simulation of possible rate paths over the next 7 days")
    fc = st.selectbox("Country", get_all_countries(), key="forest")
    fig_forest = forest(_CURRENT_RATES[fc])
    st.plotly_chart(fig_forest, use_container_width=True)
    st.markdown("---")
    c1,c2,c3 = st.columns(3)
    c1.metric("Blueprints", len(mem["designs"]), delta="+1")
    c2.metric("Concepts", len(mem["designs"])*5, delta="Evolving")
    c3.metric("Logs", len(mem["logs"]))

elif nav == "Concepts":
    if st.session_state.generated_concepts:
        concepts = st.session_state.generated_concepts
        st.markdown("## 🔬 Evolution Engine Results")
        st.caption("5 unique design concepts evaluated by Sai AI Agents")
        names = ["Alpha","Beta","Gamma","Delta","Epsilon"]
        colors = ["#888","#999","#777","#666","#555"]
        tabs = st.tabs(names[:len(concepts)])
        for idx, (tab, c) in enumerate(zip(tabs, concepts)):
            with tab:
                sc = c["scores"]; ec = c["eurocode"]
                st.markdown(f"**Design brief:** {describe_concept(c)}")
                col1, col2 = st.columns([3,2])
                with col1:
                    st.markdown("### 🗺️ 2D Floor Plan")
                    st.plotly_chart(render_floorplan(c["plan"], c["structural"]["span"]), use_container_width=True, key=f"fp_{idx}")
                    st.caption(f"Floor Area: {c['floor_area']} m² | {c['floors']} floors | {c['country']}")
                    with st.expander("🧱 Material Breakdown"): st.dataframe(boq_table(c), use_container_width=True)
                with col2:
                    for lbl, key, col in [("🏛️ Architect AI","arch","#888"),("⚙️ Structural AI","struct","#aaa"),("🌱 Sustainability AI","sust","#777"),("💰 Cost AI","cost","#999")]:
                        st.markdown(f"<div style='margin-bottom:6px;'><div style='display:flex;align-items:center;font-size:12px;color:#888'>{lbl} {sc[key]}%</div><div class='metric-bar-bg'><div class='metric-bar-fg' style='width:{sc[key]}%;background:{col};'></div></div></div>", unsafe_allow_html=True)
                    st.metric("USD Total", f"${c['total_usd']:,.0f}")
                    st.metric(f"Local ({c['fx']['currency']})", f"{c['fx']['symbol']} {c['total_local']:,.0f}")
                    st.markdown("### 📦 3D Massing")
                    view = st.radio("View", ["Isometric","Interactive"], horizontal=True, key=f"3d_{idx}")
                    if view == "Isometric": st.components.v1.html(render_isometric(c["plan"], c["structural"]["span"]), height=400)
                    else: st.plotly_chart(render_3d(c["plan"], c["floors"], c["structural"]["span"]), use_container_width=True, key=f"3d_{idx}")
        with st.expander("📊 AI Score Radar", expanded=False):
            radar_df = pd.DataFrame([{"Concept":f"{names[i]} ({c['type']})", "Architecture":c["scores"]["arch"], "Structural":c["scores"]["struct"], "Sustainability":c["scores"]["sust"], "Cost Efficiency":c["scores"]["cost"]} for i,c in enumerate(concepts)])
            cats = list(radar_df.columns[1:])
            fig_radar = go.Figure()
            for i, row in radar_df.iterrows(): fig_radar.add_trace(go.Scatterpolar(r=row[cats].values, theta=cats, fill='toself', name=row["Concept"], line_color=colors[i]))
            fig_radar.update_layout(polar=dict(radialaxis=dict(range=[0,100])), paper_bgcolor='rgba(0,0,0,0)', font_color='#aaaaaa')
            st.plotly_chart(fig_radar, use_container_width=True)
        asset = concepts[0]
        st.markdown("---"); st.markdown("### 🏆 TOP RECOMMENDATION: CONCEPT ALPHA")
        col_save, col_export = st.columns(2)
        if col_save.button("💾 Save to Library"):
            mem["designs"].append({"id":asset["id"],"type":asset["type"],"country":asset["country"],"soil":asset.get("soil_name",""),"total_gfa":asset["total_gfa"],"scores":asset["scores"],"plan":asset["plan"],"timestamp":datetime.now().isoformat()})
            save_memory(username, mem); st.success("Design saved!")
        with col_export:
            exp = pd.DataFrame([{"ID":c["id"],"Type":c["type"],"Country":c["country"],"Soil":c.get("soil_name",""),"GFA":c["total_gfa"],"Floors":c["floors"],"Rooms":len(c["plan"]),"Cost USD":c["total_usd"],"Cost Local":c["total_local"],"Arch%":c["scores"]["arch"],"Struct%":c["scores"]["struct"],"Sust%":c["scores"]["sust"],"CostEff%":c["scores"]["cost"],"Composite":c["scores"]["composite"]} for c in concepts])
            st.download_button("📥 Export CSV", exp.to_csv(index=False).encode(), file_name="arc_concepts.csv", mime="text/csv")
        with st.expander("📅 Construction Gantt Chart"): st.plotly_chart(gantt_chart(asset), use_container_width=True)
    else: st.info("No designs generated yet. Configure parameters in sidebar and click **Generate Concepts**.")

elif nav == "Ram AI":
    st.markdown("## 🧠 Ram AI – Infinite Architectural Intelligence")
    st.markdown("Ask Ram anything about construction, soil, costs, or design in East Africa.")
    with st.form("ram_form"):
        q = st.text_input("Your question:", placeholder="Ask Ram about soil, foundations, costs...")
        submitted = st.form_submit_button("Ask Ram AI")
    if submitted and q:
        with st.spinner("Ram is thinking..."):
            resp = ram_ai(q, country, domain)
            st.session_state.ram_history.append(("You", q))
            st.session_state.ram_history.append(("Ram", resp))
    for speaker, msg in st.session_state.ram_history:
        if speaker == "You": st.markdown(f"**👤 {speaker}:** {msg}")
        else: st.markdown(f'**🧠 {speaker}:** {msg}')

st.markdown("<div style='text-align:center;padding:20px 0;color:#444'>AI Powered · Data Driven · Secure · Scalable</div>", unsafe_allow_html=True)
