# =========================================================
# 🏗️ RANDOM AI v20 — STRUCTURAL DESIGN CORE
# Architecture + Eurocode-inspired logic + 3D extrusion
# =========================================================

import streamlit as st
import numpy as np
import random
import matplotlib.pyplot as plt

from mpl_toolkits.mplot3d import Axes3D

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(page_title="Random AI v20", layout="wide")

st.title("🏗️ Random AI v20 — Structural Design Core")
st.caption("Procedural architecture with simplified Eurocode-inspired logic and structural awareness")

# =========================================================
# BUILDING TYPES
# =========================================================

BUILDING_TYPES = ["Residential", "Commercial", "Industrial"]

# Structural load assumptions (simplified kN/m2)
LIVE_LOADS = {
    "Residential": 2.0,
    "Commercial": 4.0,
    "Industrial": 7.5
}

# =========================================================
# STRUCTURAL GRID ENGINE
# =========================================================

def generate_grid(width, depth, spacing=4):
    x_lines = np.arange(0, width + spacing, spacing)
    y_lines = np.arange(0, depth + spacing, spacing)
    return x_lines, y_lines

# =========================================================
# FLOOR PLAN GENERATOR
# =========================================================

def generate_floor_plan(building_type, width, depth, floors):
    plan = []

    for f in range(floors):
        if building_type == "Residential":
            rooms = random.randint(2, 5)
        elif building_type == "Commercial":
            rooms = random.randint(4, 10)
        else:
            rooms = random.randint(1, 3)

        floor = {
            "floor": f + 1,
            "rooms": rooms,
            "core": "central" if building_type != "Industrial" else "offset"
        }
        plan.append(floor)

    return plan

# =========================================================
# STRUCTURAL CHECK (SIMPLIFIED EUROCODE STYLE)
# =========================================================

def structural_check(spans, load_type, beam_capacity=30):
    """
    Simplified logic:
    - higher load + longer span reduces safety margin
    """

    load = LIVE_LOADS[load_type]
    results = []

    for span in spans:
        demand = load * span
        utilization = demand / beam_capacity

        status = "OK" if utilization < 1 else "OVERSTRESSED"

        results.append({
            "span": span,
            "load": load,
            "utilization": round(utilization, 2),
            "status": status
        })

    return results

# =========================================================
# 3D BUILDING EXTRUSION
# =========================================================

def plot_building_3d(width, depth, floors, grid_spacing=4):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    x_lines, y_lines = generate_grid(width, depth, grid_spacing)

    # Draw grid
    for x in x_lines:
        ax.plot([x, x], [0, depth], [0, 0], color="gray", linewidth=0.5)
    for y in y_lines:
        ax.plot([0, width], [y, y], [0, 0], color="gray", linewidth=0.5)

    # Extrude floors
    floor_height = 3

    for f in range(floors + 1):
        z = f * floor_height

        # perimeter slab
        ax.plot([0, width, width, 0, 0],
                [0, 0, depth, depth, 0],
                [z, z, z, z, z],
                color="black")

        # vertical columns
        for x in x_lines:
            for y in y_lines:
                ax.plot([x, x], [y, y], [0, z], color="lightblue", linewidth=0.3)

    ax.set_xlabel("Width")
    ax.set_ylabel("Depth")
    ax.set_zlabel("Height")

    return fig

# =========================================================
# UI CONTROLS
# =========================================================

col1, col2, col3 = st.columns(3)

with col1:
    building_type = st.selectbox("Building Type", BUILDING_TYPES)

with col2:
    floors = st.slider("Number of Floors", 1, 20, 5)

with col3:
    grid_spacing = st.slider("Structural Grid Spacing", 2, 8, 4)

width = st.slider("Building Width", 10, 60, 30)
depth = st.slider("Building Depth", 10, 60, 25)

# =========================================================
# GENERATE SYSTEM
# =========================================================

if st.button("Generate Structure"):

    st.subheader("🏢 Floor Plan Logic")

    plan = generate_floor_plan(building_type, width, depth, floors)
    st.json(plan)

    st.subheader("🧱 Structural Grid")

    xg, yg = generate_grid(width, depth, grid_spacing)

    fig, ax = plt.subplots()
    for x in xg:
        ax.plot([x, x], [0, depth])
    for y in yg:
        ax.plot([0, width], [y, y])

    ax.set_title("Structural Grid Layout")
    st.pyplot(fig)

    st.subheader("⚙️ Eurocode-Inspired Structural Check")

    spans = [grid_spacing for _ in range(len(xg) - 1)]
    results = structural_check(spans, building_type)

    st.dataframe(results)

    st.subheader("🏗️ 3D Structural Model")

    fig3d = plot_building_3d(width, depth, floors, grid_spacing)
    st.pyplot(fig3d)

# =========================================================
# FOOTER
# =========================================================

st.caption("Random AI v20 — structural logic layer active. Geometry now carries intent.")
