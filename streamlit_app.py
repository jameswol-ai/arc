import streamlit as st
import random
import json
import time

# =========================================================
# 🏗️ RANDOM — ARCH + EUROCODE ENGINE (INTEGRATED)
# =========================================================

st.set_page_config(page_title="Random Eurocode AI v6", layout="wide")

st.title("🏗️🧬 Random AI — Architectural + Eurocode System")
st.caption("Geometry → Loads → Structure → Survival")

# =========================================================
# SIDEBAR INPUTS (ARCHITECTURE DRIVES STRUCTURE)
# =========================================================

st.sidebar.header("🏗️ Architectural Parameters")

BASE_SPAN = st.sidebar.slider("Span (m)", 4, 30, 12)
BASE_DEPTH = st.sidebar.slider("Depth (m)", 4, 30, 10)
BASE_FLOORS = st.sidebar.slider("Floors", 1, 15, 4)

material_bias = st.sidebar.selectbox("Material", ["Concrete", "Steel"])

live_load = st.sidebar.slider("Live Load Q (kN/m²)", 1, 10, 5)
wind_base = st.sidebar.slider("Base Wind (kN/m²)", 0, 5, 2)

auto_mode = st.sidebar.checkbox("🔄 Auto Evolution", True)
speed = st.sidebar.slider("Speed", 0.2, 2.0, 0.8)

# Eurocode partial factors (EN 1990)
gamma_G = 1.35
gamma_Q = 1.5

# =========================================================
# LOAD MODEL (EN 1991 — GEOMETRY DEPENDENT)
# =========================================================

def dead_load(material):
    return 5.5 if material == "Concrete" else 3.0

def wind_load(height):
    # wind increases with height (simplified EN 1991 concept)
    return wind_base * (1 + height / 30)

def load_combinations(Gk, Qk, Wk):
    ULS = gamma_G * Gk + gamma_Q * Qk + 1.5 * Wk
    SLS = Gk + Qk + Wk
    return ULS, SLS

# =========================================================
# STRUCTURAL ANALYSIS (EC2 / EC3 STYLE)
# =========================================================

def beam_analysis(span, depth, ULS, material):
    q = ULS * depth
    M = q * span**2 / 8  # kNm

    if material == "Steel":
        fy = 355
        W_req = M * 1e6 / fy
        W_cap = 200e6
    else:
        fcd = 25
        W_req = M * 1e6 / fcd
        W_cap = 300e6

    util = W_req / W_cap
    return M, util

def column_analysis(area, floors, ULS, material):
    N = ULS * area * floors

    capacity = 80000 if material == "Concrete" else 50000
    util = N / capacity

    return N, util

def deflection_check(span, depth):
    ratio = span / max(depth, 1)
    if ratio > 3:
        return 1.0
    elif ratio > 2:
        return 0.5
    return 0.2

def lateral_check(height, depth):
    slender = height / max(depth, 1)
    if slender > 6:
        return 1.0
    elif slender > 4:
        return 0.5
    return 0.2

# =========================================================
# 🏗️ ARCHITECTURAL GENERATION (DRIVES EVERYTHING)
# =========================================================

def generate_building():
    span = max(4, BASE_SPAN + random.randint(-3, 3))
    depth = max(4, BASE_DEPTH + random.randint(-3, 3))
    floors = max(1, BASE_FLOORS + random.randint(-2, 4))

    material = material_bias if random.random() > 0.3 else random.choice(["Concrete", "Steel"])

    height = floors * 3
    area = span * depth

    Gk = dead_load(material)
    Qk = random.uniform(1, 10)
    Wk = wind_load(height)

    ULS, SLS = load_combinations(Gk, Qk, Wk)

    return {
        "span": span,
        "depth": depth,
        "floors": floors,
        "height": height,
        "area": area,
        "material": material,
        "loads": {
            "Gk": Gk,
            "Qk": Qk,
            "Wk": Wk,
            "ULS": ULS,
            "SLS": SLS
        }
    }

# =========================================================
# 🧠 EVALUATION (EUROCODE DRIVEN)
# =========================================================

def evaluate(b):
    span = b["span"]
    depth = b["depth"]
    height = b["height"]
    area = b["area"]
    mat = b["material"]

    ULS = b["loads"]["ULS"]
    SLS = b["loads"]["SLS"]

    # structural checks
    M, beam_util = beam_analysis(span, depth, ULS, mat)
    N, col_util = column_analysis(area, b["floors"], ULS, mat)

    defl = deflection_check(span, depth)
    lateral = lateral_check(height, depth)

    # Eurocode logic: utilization > 1 = fail
    beam_pen = 0 if beam_util > 1 else (1 - beam_util) * 10
    col_pen = 0 if col_util > 1 else (1 - col_util) * 10

    score = (
        beam_pen * 0.3 +
        col_pen * 0.3 +
        (1 - defl) * 5 +
        (1 - lateral) * 5
    )

    return {
        "score": score,
        "moment": M,
        "beam_util": beam_util,
        "col_util": col_util,
        "deflection": defl,
        "lateral": lateral
    }

# =========================================================
# 🏗️ FLOORPLAN (ARCHITECTURE OUTPUT)
# =========================================================

def floorplan(span, depth):
    grid = []
    for y in range(depth):
        row = ""
        for x in range(span):
            if x in [0, span-1] or y in [0, depth-1]:
                row += "█"
            elif x % 4 == 0 and y % 4 == 0:
                row += "●"
            elif x % 4 == 0 or y % 4 == 0:
                row += "╬"
            else:
                row += " "
        grid.append(row)
    return "\n".join(grid)

# =========================================================
# 🧬 EVOLUTION (SELECTION + MUTATION + CROSSOVER)
# =========================================================

def crossover(a, b):
    return {
        "span": random.choice([a["span"], b["span"]]),
        "depth": random.choice([a["depth"], b["depth"]]),
        "floors": random.choice([a["floors"], b["floors"]]),
        "height": random.choice([a["height"], b["height"]]),
        "area": random.choice([a["area"], b["area"]]),
        "material": random.choice([a["material"], b["material"]]),
        "loads": a["loads"]
    }

def evolve(city):
    new = []
    best = []

    for b in city:
        r = evaluate(b)
        score = r["score"]

        if score > 5:
            new.append(b)

            if score > 8:
                # mutation
                new.append(generate_building())
                best.append((score, b))

                # crossover
                if len(city) > 1:
                    partner = random.choice(city)
                    new.append(crossover(b, partner))
        else:
            new.append(generate_building())

    return new, best

# =========================================================
# STATE
# =========================================================

if "city" not in st.session_state:
    st.session_state.city = []
if "memory" not in st.session_state:
    st.session_state.memory = []
if "tick" not in st.session_state:
    st.session_state.tick = 0

# =========================================================
# CONTROLS
# =========================================================

c1, c2, c3 = st.columns(3)

with c1:
    if st.button("🏗️ Spawn"):
        st.session_state.city.append(generate_building())

with c2:
    if st.button("▶ Evolve"):
        new, best = evolve(st.session_state.city)
        st.session_state.city = new
        st.session_state.memory += best
        st.session_state.tick += 1

with c3:
    if st.button("🧱 Reset"):
        st.session_state.city = []
        st.session_state.memory = []
        st.session_state.tick = 0

# =========================================================
# AUTO LOOP
# =========================================================

if auto_mode and st.session_state.city:
    new, best = evolve(st.session_state.city)
    st.session_state.city = new
    st.session_state.memory += best
    st.session_state.tick += 1
    time.sleep(speed)
    st.rerun()

# =========================================================
# DISPLAY
# =========================================================

st.subheader(f"🏙️ Tick: {st.session_state.tick}")

for i, b in enumerate(st.session_state.city):
    r = evaluate(b)

    status = "🟢 PASS"
    if r["beam_util"] > 1 or r["col_util"] > 1:
        status = "🔴 FAIL"

    st.markdown(f"### Building {i+1} — {status}")

    st.write(f"{b['material']} | {b['floors']} floors | {b['span']}m x {b['depth']}m")

    st.write(f"Score: {round(r['score'],2)}")
    st.write(f"Moment: {round(r['moment'],2)} kNm")
    st.write(f"Beam Util: {round(r['beam_util'],2)} | Column Util: {round(r['col_util'],2)}")

    st.text(floorplan(b["span"], b["depth"]))

# =========================================================
# EXPORT
# =========================================================

st.download_button(
    "📦 Export City",
    json.dumps(st.session_state.city, indent=2),
    "city.json"
)
