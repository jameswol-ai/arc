import streamlit as st
import random
import math
import time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# =========================================================
# 🏗️ RANDOM AI — ARCHITECTURE + STRUCTURAL EVOLUTION CORE v18
# =========================================================

st.set_page_config(page_title="Random AI Architecture System v18", layout="wide")

st.title("🏗️ Random AI v18 — Structural Evolution Intelligence")
st.caption("A senior-level generative architecture system with evolving structural memory")

# =========================================================
# STATE INIT
# =========================================================
if "running" not in st.session_state:
    st.session_state.running = False

if "stability" not in st.session_state:
    st.session_state.stability = 0.65

if "history" not in st.session_state:
    st.session_state.history = []

if "tick" not in st.session_state:
    st.session_state.tick = 0


# =========================================================
# SIDEBAR — SYSTEM CONTROLS
# =========================================================
st.sidebar.header("System Parameters")

floors = st.sidebar.slider("Floors", 1, 60, 10)
width = st.sidebar.slider("Width (m)", 5, 120, 30)
depth = st.sidebar.slider("Depth (m)", 5, 120, 20)

material = st.sidebar.selectbox("Material", ["Concrete", "Steel", "Timber", "Hybrid"])
importance = st.sidebar.selectbox("Importance Class", ["Low", "Normal", "High"])

load_factor = st.sidebar.slider("Live Load (kN/m²)", 1.0, 12.0, 3.0)
dead_factor = st.sidebar.slider("Dead Load Factor", 0.5, 3.0, 1.2)
mutation = st.sidebar.slider("Mutation Rate", 0.0, 1.0, 0.2)

env_stress = st.sidebar.slider("Environmental Stress (wind + heat)", 0.0, 1.0, 0.35)


# =========================================================
# 🏗️ STRUCTURAL ENGINE (EUROCODE-INSPIRED SIMPLIFIED)
# =========================================================
def structural_model():
    area = width * depth

    strength_map = {
        "Concrete": 55,
        "Steel": 120,
        "Timber": 35,
        "Hybrid": 80
    }

    importance_map = {
        "Low": 0.9,
        "Normal": 1.0,
        "High": 1.25
    }

    strength = strength_map[material]
    imp = importance_map[importance]

    dead_load = area * floors * dead_factor * imp
    live_load = area * floors * load_factor * imp

    total_load = dead_load + live_load

    # environmental penalty (wind + heat + inefficiency)
    env_penalty = total_load * env_stress * 0.15

    adjusted_load = total_load + env_penalty

    capacity = area * strength * 1.05

    utilization = adjusted_load / capacity
    stability = max(0.0, 1.0 - utilization)

    return {
        "total_load": adjusted_load,
        "capacity": capacity,
        "utilization": utilization,
        "stability": stability
    }


# =========================================================
# 🧬 EVOLUTION ENGINE (SMOOTHED MEMORY DRIFT)
# =========================================================
def evolve(current, target, mutation_rate):
    noise = np.random.normal(0, mutation_rate * 0.1)
    blended = 0.85 * current + 0.15 * target + noise
    return float(np.clip(blended, 0, 1))


# =========================================================
# 🏛️ FLOORPLAN GENERATOR (ZONED LOGIC)
# =========================================================
def generate_plan():
    zones = ["PUBLIC", "SEMI", "PRIVATE", "STRUCTURAL_CORE"]

    def zone_symbol(z):
        return {
            "PUBLIC": "▣",
            "SEMI": "▤",
            "PRIVATE": "▥",
            "STRUCTURAL_CORE": "█"
        }[z]

    return [
        [
            [zone_symbol(random.choice(zones)) for _ in range(7)]
            for _ in range(7)
        ]
        for _ in range(floors)
    ]


# =========================================================
# 🧠 CORE SIMULATION STEP
# =========================================================
def simulation_step():
    analysis = structural_model()

    # evolve system stability
    st.session_state.stability = evolve(
        st.session_state.stability,
        analysis["stability"],
        mutation
    )

    st.session_state.history.append(st.session_state.stability)

    if len(st.session_state.history) > 60:
        st.session_state.history.pop(0)

    return analysis


analysis = structural_model()
floorplans = generate_plan()


# =========================================================
# CONTROL PANEL
# =========================================================
colA, colB = st.columns(2)

with colA:
    if st.button("🚀 Start Evolution Engine"):
        st.session_state.running = True

with colB:
    if st.button("🛑 Stop Engine"):
        st.session_state.running = False


# =========================================================
# DASHBOARD
# =========================================================
col1, col2, col3 = st.columns(3)

# -------------------------
# STRUCTURAL CORE
# -------------------------
with col1:
    st.subheader("📐 Structural System")

    st.metric("Total Load", f"{analysis['total_load']:.1f}")
    st.metric("Capacity", f"{analysis['capacity']:.1f}")
    st.metric("Utilization", f"{analysis['utilization']:.3f}")
    st.metric("Stability", f"{analysis['stability']:.3f}")

    if analysis["stability"] > 0.75:
        st.success("Stable structural regime")
    elif analysis["stability"] > 0.45:
        st.warning("Increasing structural stress")
    else:
        st.error("Critical instability zone")


# -------------------------
# FLOOR SYSTEM
# -------------------------
with col2:
    st.subheader("🏗️ Spatial System (Zoned Architecture)")

    for i, floor in enumerate(floorplans):
        st.text(f"Level {i+1}")
        for row in floor:
            st.text(" ".join(row))


# -------------------------
# EVOLUTION CORE
# -------------------------
with col3:
    st.subheader("🧬 Evolution State")

    st.write("System Stability")
    st.progress(st.session_state.stability)

    st.write("Structural Response")
    st.progress(analysis["stability"])

    harmony = (st.session_state.stability + analysis["stability"]) / 2

    st.write("System Harmony")
    st.progress(harmony)


# =========================================================
# EVOLUTION LOOP
# =========================================================
if st.session_state.running:
    st.info("🧬 Evolution running — structural adaptation in progress...")

    analysis = simulation_step()
    st.session_state.tick += 1

    st.toast(f"Generation {st.session_state.tick}")

    time.sleep(0.25)
    st.rerun()


# =========================================================
# HISTORY GRAPH
# =========================================================
st.divider()
st.subheader("📊 Stability Evolution Timeline")

fig, ax = plt.subplots()
ax.plot(st.session_state.history)
ax.set_title("Structural Stability Over Time")
ax.set_xlabel("Generations")
ax.set_ylabel("Stability Index")

st.pyplot(fig)


# =========================================================
# MANUAL STEP
# =========================================================
st.divider()
st.subheader("🌍 Manual Simulation Step")

if st.button("Run Single Evolution Step"):
    analysis = simulation_step()
    st.success(f"Step complete — stability: {st.session_state.stability:.3f}")
