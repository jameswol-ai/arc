# =========================================================
# 🏗️ RANDOM AI v20 — STRUCTURAL ENGINEERING MODE
# Columns + Beams + Load Paths + Evolutionary Architecture
# =========================================================

import streamlit as st
import numpy as np
import random
import time
import matplotlib.pyplot as plt

st.set_page_config(page_title="Random AI v20", layout="wide")

st.title("🏗️ Random AI v20 — Engineering Structural Intelligence")
st.caption("Now simulating simplified structural mechanics, not just geometry")

# =========================================================
# STATE
# =========================================================
if "running" not in st.session_state:
    st.session_state.running = False

if "stability" not in st.session_state:
    st.session_state.stability = 0.7

if "history" not in st.session_state:
    st.session_state.history = []

if "tick" not in st.session_state:
    st.session_state.tick = 0


# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.header("Engineering Parameters")

floors = st.sidebar.slider("Floors", 1, 80, 12)
span = st.sidebar.slider("Structural Grid Span (m)", 2, 12, 4)
width = st.sidebar.slider("Building Width (m)", 10, 120, 40)
depth = st.sidebar.slider("Building Depth (m)", 10, 120, 30)

material_factor = st.sidebar.selectbox("Material System", ["Concrete", "Steel", "Hybrid"])
wind = st.sidebar.slider("Wind Load Factor", 0.0, 1.0, 0.4)
mutation = st.sidebar.slider("Structural Mutation", 0.0, 1.0, 0.25)


# =========================================================
# 🧠 STRUCTURAL ENGINE (SIMPLIFIED ENGINEERING)
# =========================================================
def structural_model():

    area = width * depth

    strength_map = {
        "Concrete": 60,
        "Steel": 120,
        "Hybrid": 90
    }

    strength = strength_map[material_factor]

    base_load = area * floors * 4.5

    # 🌪️ wind + height amplification
    lateral_load = floors * wind * base_load * 0.1

    total_load = base_load + lateral_load

    capacity = area * strength

    utilization = total_load / max(capacity, 1e-6)
    stability = max(0.0, 1.0 - utilization)

    return {
        "load": total_load,
        "capacity": capacity,
        "utilization": utilization,
        "stability": stability
    }


# =========================================================
# 🧬 EVOLUTION ENGINE
# =========================================================
def evolve(current, target, mutation_rate):
    noise = np.random.normal(0, mutation_rate * 0.05)
    return float(np.clip(0.8 * current + 0.2 * target + noise, 0, 1))


# =========================================================
# 🧱 COLUMN–BEAM GRID SYSTEM (NEW CORE)
# =========================================================
def generate_structure():

    grid_x = max(2, int(width / span))
    grid_y = max(2, int(depth / span))

    structure = []

    for f in range(floors):

        floor = {
            "columns": [],
            "beams": []
        }

        # columns
        for i in range(grid_x):
            for j in range(grid_y):
                floor["columns"].append((i, j))

        # beams (connect adjacent columns)
        for i in range(grid_x - 1):
            for j in range(grid_y - 1):
                floor["beams"].append(
                    ((i, j), (i + 1, j))
                )
                floor["beams"].append(
                    ((i, j), (i, j + 1))
                )

        structure.append(floor)

    return structure


# =========================================================
# LOAD PATH SIMULATION (SIMPLIFIED)
# =========================================================
def load_distribution():

    base = structural_model()

    load_per_column = base["load"] / max(1, (width / span) * (depth / span) * floors)

    return {
        "column_load": load_per_column,
        "stress_level": min(1.0, load_per_column / (base["capacity"] / 10))
    }


# =========================================================
# SIMULATION STEP
# =========================================================
def simulation_step():

    analysis = structural_model()

    st.session_state.stability = evolve(
        st.session_state.stability,
        analysis["stability"],
        mutation
    )

    st.session_state.history.append(st.session_state.stability)

    if len(st.session_state.history) > 100:
        st.session_state.history.pop(0)

    return analysis


analysis = structural_model()
structure = generate_structure()
loads = load_distribution()


# =========================================================
# CONTROL
# =========================================================
cA, cB = st.columns(2)

with cA:
    if st.button("🚀 Start Engineering Simulation"):
        st.session_state.running = True

with cB:
    if st.button("🛑 Stop"):
        st.session_state.running = False


# =========================================================
# DASHBOARD
# =========================================================
a1, a2, a3 = st.columns(3)

# -------------------------
# STRUCTURE
# -------------------------
with a1:
    st.subheader("🏗️ Structural Engine")

    st.metric("Load", f"{analysis['load']:.1f}")
    st.metric("Capacity", f"{analysis['capacity']:.1f}")
    st.metric("Utilization", f"{analysis['utilization']:.3f}")
    st.metric("Stability", f"{analysis['stability']:.3f}")

    if analysis["stability"] > 0.75:
        st.success("Structurally safe")
    elif analysis["stability"] > 0.45:
        st.warning("Stress increasing")
    else:
        st.error("Failure risk zone")


# -------------------------
# GRID SYSTEM
# -------------------------
with a2:
    st.subheader("🧱 Column–Beam Grid")

    f0 = structure[0]

    st.write("Columns:", len(f0["columns"]))
    st.write("Beams:", len(f0["beams"]))

    st.write("Sample Columns:")
    st.text(f0["columns"][:10])


# -------------------------
# LOAD PATH
# -------------------------
with a3:
    st.subheader("📊 Load Distribution")

    st.metric("Column Load", f"{loads['column_load']:.2f}")
    st.metric("Stress Level", f"{loads['stress_level']:.2f}")

    st.progress(min(1.0, loads["stress_level"]))


# =========================================================
# LOOP
# =========================================================
if st.session_state.running:

    simulation_step()
    st.session_state.tick += 1

    st.toast(f"Engine Cycle {st.session_state.tick}")

    time.sleep(0.2)
    st.rerun()


# =========================================================
# HISTORY
# =========================================================
st.divider()
st.subheader("📈 Stability Evolution")

if len(st.session_state.history) > 1:
    fig, ax = plt.subplots()
    ax.plot(st.session_state.history)
    ax.set_title("Structural Stability Over Time")
    st.pyplot(fig)


# =========================================================
# MANUAL STEP
# =========================================================
st.divider()

if st.button("Run Single Engineering Step"):
    simulation_step()
    st.success(f"Stability: {st.session_state.stability:.3f}")
