import streamlit as st
import random
import math

# =========================================================
# 🧬 RANDOM AI — ARCHITECTURE + STRUCTURAL ENGINE
# =========================================================

st.set_page_config(page_title="Random Architecture AI", layout="wide")

st.title("🏗️ Random AI — Living Architectural + Structural System")
st.caption("Generates floorplans, applies simplified Eurocode-style checks, and evolves designs")

# =========================================================
# SIDEBAR — BUILD PARAMETERS
# =========================================================

st.sidebar.header("🏢 Building Parameters")

floors = st.sidebar.slider("Number of floors", 1, 20, 3)
width = st.sidebar.slider("Building width (m)", 5, 50, 20)
length = st.sidebar.slider("Building length (m)", 5, 80, 30)
load_per_floor = st.sidebar.slider("Live load per floor (kN/m²)", 1.0, 10.0, 3.0)
material_strength = st.sidebar.slider("Material strength (MPa)", 10, 60, 25)

mutation_mode = st.sidebar.checkbox("🧬 Enable Random Evolution Mode", value=False)

# =========================================================
# FLOORPLAN GENERATION
# =========================================================

def generate_floorplan(width, length, floors):
    plan = []
    for f in range(floors):
        grid = []
        for x in range(int(width // 2)):
            row = []
            for y in range(int(length // 2)):
                cell = random.choice(["□", "□", "□", "■"])  # walls vs space
                row.append(cell)
            grid.append(row)
        plan.append(grid)
    return plan

def mutate_floorplan(plan):
    new_plan = []
    for floor in plan:
        new_floor = []
        for row in floor:
            new_row = []
            for cell in row:
                if random.random() < 0.1:
                    new_row.append("■" if cell == "□" else "□")
                else:
                    new_row.append(cell)
            new_floor.append(new_row)
        new_plan.append(new_floor)
    return new_plan

# =========================================================
# STRUCTURAL ANALYSIS (EUROCODE-INSPIRED SIMPLIFIED MODEL)
# =========================================================

def structural_check(width, length, floors, load, strength):
    area = width * length
    total_load = load * area * floors

    # Simplified stress model
    stress = total_load / (area * 0.6)  # assumed load distribution factor

    safety_factor = strength / (stress / 1000)  # MPa conversion approximation

    status = "SAFE 🟢" if safety_factor > 1.5 else "WARNING 🟠" if safety_factor > 1.0 else "FAIL 🔴"

    return {
        "total_load": total_load,
        "stress": stress,
        "safety_factor": safety_factor,
        "status": status
    }

# =========================================================
# DISPLAY FLOORPLAN
# =========================================================

def display_plan(plan):
    for i, floor in enumerate(plan):
        st.subheader(f"Floor {i + 1}")
        for row in floor:
            st.text(" ".join(row))

# =========================================================
# MAIN ENGINE
# =========================================================

if "plan" not in st.session_state:
    st.session_state.plan = generate_floorplan(width, length, floors)

if st.sidebar.button("🏗️ Generate New Design"):
    st.session_state.plan = generate_floorplan(width, length, floors)

if mutation_mode:
    if st.sidebar.button("🧬 Evolve Design"):
        st.session_state.plan = mutate_floorplan(st.session_state.plan)

# =========================================================
# STRUCTURAL OUTPUT
# =========================================================

result = structural_check(width, length, floors, load_per_floor, material_strength)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Load (kN)", round(result["total_load"], 2))

with col2:
    st.metric("Stress Proxy", round(result["stress"], 2))

with col3:
    st.metric("Safety Factor", round(result["safety_factor"], 2))

st.subheader("🧪 Structural Status")
st.write(result["status"])

# =========================================================
# FLOORPLAN VISUALIZATION
# =========================================================

st.subheader("🏢 Generated Floorplan")

display_plan(st.session_state.plan)

# =========================================================
# RANDOM AI SIGNATURE
# =========================================================

st.markdown("---")
st.caption("Random AI: architecture is no longer static. It is evolving geometry.")
