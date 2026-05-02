import streamlit as st
import random
import json

# =========================================================
# 🏗️ RANDOM — ARCHITECT + STRUCTURAL ANALYZER
# =========================================================

st.set_page_config(page_title="Random Architecture + Eurocode AI", layout="wide")

st.title("🏗️ Random AI — Architecture + Structural Eurocode Engine")
st.caption("Parametric design + structural analysis + evolutionary improvement loop")

# =========================================================
# USER INPUT PANEL
# =========================================================

st.sidebar.header("🏗️ Building Parameters")

span = st.sidebar.slider("Span (m)", 4, 30, 12)
depth = st.sidebar.slider("Depth (m)", 4, 30, 10)
floors = st.sidebar.slider("Floors", 1, 10, 3)

material = st.sidebar.selectbox("Material", ["Reinforced Concrete", "Steel"])

live_load = st.sidebar.slider("Live Load Q (kN/m²)", 1, 10, 5)
wind_load = st.sidebar.slider("Wind Load W (kN/m²)", 0, 10, 3)

safety_mode = st.sidebar.selectbox("Safety Level", ["Normal", "High Safety", "Experimental"])

# =========================================================
# SAFETY FACTORS (Eurocode-inspired)
# =========================================================

if safety_mode == "Normal":
    gamma_g = 1.35
    gamma_q = 1.5
elif safety_mode == "High Safety":
    gamma_g = 1.5
    gamma_q = 1.7
else:
    gamma_g = 1.2
    gamma_q = 1.3

# =========================================================
# LOAD MODEL (Eurocode-inspired EN 1990 / EN 1991)
# =========================================================

def dead_load(mat):
    return 5.5 if mat == "Reinforced Concrete" else 3.0

Gk = dead_load(material)
Qk = live_load
Wk = wind_load

# Ultimate Limit State (ULS)
ULS = gamma_g * Gk + gamma_q * Qk + 1.5 * Wk

# Serviceability Limit State (SLS)
SLS = Gk + Qk + Wk

# =========================================================
# STRUCTURAL ENGINE
# =========================================================

def slenderness(h, s):
    return h / max(s, 0.1)

def stability_score(h, s, uls):
    sl = slenderness(h, s)

    if sl > 1.2 or uls > 85:
        return 2
    elif sl > 0.8 or uls > 60:
        return 5
    return 9

def deflection_risk(span, depth):
    ratio = span / max(depth, 1)
    if ratio > 3:
        return 8
    elif ratio > 2:
        return 6
    return 3

def utilization(uls, capacity=100):
    return (uls / capacity) * 10

def eurocode_assessment():
    stab = stability_score(depth, span, ULS)
    defl = deflection_risk(span, depth)
    util = utilization(ULS)

    return stab, defl, util

# =========================================================
# ARCHITECTURE GENERATION
# =========================================================

def generate_floorplan(span, depth, grid=4):
    layout = []

    for y in range(depth):
        row = ""
        for x in range(span):

            # boundary walls
            if x == 0 or y == 0 or x == span - 1 or y == depth - 1:
                row += "█"

            # structural columns grid
            elif x % grid == 0 and y % grid == 0:
                row += "●"

            # core zone (stairs/elevator)
            elif span//2 - 1 <= x <= span//2 + 1 and depth//2 - 1 <= y <= depth//2 + 1:
                row += "■"

            # beams
            elif x % grid == 0 or y % grid == 0:
                row += "╬"

            else:
                row += " "

        layout.append(row)

    return "\n".join(layout)

# =========================================================
# DESIGN ENGINE
# =========================================================

def design_building():
    return {
        "span": span,
        "depth": depth,
        "floors": floors,
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
# UI ACTIONS
# =========================================================

if "city" not in st.session_state:
    st.session_state.city = []
    st.session_state.tick = 0

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🏗️ Generate Building"):
        st.session_state.city.append(design_building())

with col2:
    if st.button("▶ Evolve System"):
        new_city = []

        for b in st.session_state.city:
            stab, defl, util = eurocode_assessment()

            score = (stab * 0.5 + (10 - defl) * 0.3 + (10 - util) * 0.2)

            if score > 6:
                new_city.append(b)

                if score > 8:
                    mutated = b.copy()
                    mutated["span"] += random.randint(-1, 2)
                    mutated["depth"] += random.randint(-1, 2)
                    new_city.append(mutated)
            else:
                # redesign weak structures
                new_city.append(design_building())

        st.session_state.city = new_city
        st.session_state.tick += 1

with col3:
    if st.button("🧱 Reset"):
        st.session_state.city = []
        st.session_state.tick = 0

# =========================================================
# OUTPUT
# =========================================================

st.subheader(f"🏙️ System Tick: {st.session_state.tick}")

if not st.session_state.city:
    st.info("No buildings yet — generate one to begin.")
else:
    for i, b in enumerate(st.session_state.city):

        stab, defl, util = eurocode_assessment()

        score = (stab * 0.5 + (10 - defl) * 0.3 + (10 - util) * 0.2)

        status = "🟢 SAFE"
        if score < 5:
            status = "🔴 FAIL"
        elif score < 7:
            status = "🟡 MARGINAL"

        st.markdown(f"### 🏗️ Building {i+1} — {status}")

        st.write(
            f"Span: {b['span']} | Depth: {b['depth']} | Floors: {b['floors']} | "
            f"Material: {b['material']}"
        )

        st.write(
            f"ULS: {round(ULS,2)} | SLS: {round(SLS,2)} | "
            f"Stability: {round(stab,2)} | Deflection: {round(defl,2)} | Utilization: {round(util,2)}"
        )

        st.text(generate_floorplan(b["span"], b["depth"]))

# =========================================================
# EXPORT (BIM-LIKE STRUCTURE)
# =========================================================

st.download_button(
    "📦 Export BIM Model",
    json.dumps(st.session_state.city, indent=2),
    file_name="random_bim_city.json",
    mime="application/json"
)

# =========================================================
# SYSTEM HEALTH
# =========================================================

if st.session_state.city:
    avg_score = sum(
        stability_score(depth, span, ULS)
        for _ in st.session_state.city
    ) / len(st.session_state.city)

    if avg_score > 7:
        st.success("🏛️ Structurally coherent evolving architecture system")
    else:
        st.warning("⚠ System still exploring structural stability space")
