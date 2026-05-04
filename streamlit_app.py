import streamlit as st
import random
import math
import time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# =========================================================
# 🏗️ RANDOM AI — ARCHITECTURE + EUROCODE SIMULATION CORE
# =========================================================

st.set_page_config(page_title="Random AI Architecture System", layout="wide")

st.title("🏗️ Random AI — Architectural + Structural Intelligence Dashboard")
st.caption("A living system evolving structural forms under simplified Eurocode-like logic")

# =========================================================
# SESSION STATE INIT (CRITICAL FOR EVOLUTION LOOP)
# =========================================================
if "running" not in st.session_state:
    st.session_state.running = False

if "stability" not in st.session_state:
    st.session_state.stability = 0.6

if "history" not in st.session_state:
    st.session_state.history = []

if "tick" not in st.session_state:
    st.session_state.tick = 0

# =========================================================
# SIDEBAR PARAMETERS
# =========================================================
st.sidebar.header("Building Configuration")

floors = st.sidebar.slider("Floors", 1, 60, 8)
width = st.sidebar.slider("Width (m)", 5, 120, 25)
depth = st.sidebar.slider("Depth (m)", 5, 120, 18)

material = st.sidebar.selectbox("Material", ["Concrete", "Steel", "Timber", "Hybrid"])
importance = st.sidebar.selectbox("Importance Class", ["Low", "Normal", "High"])

live_load = st.sidebar.slider("Live Load (kN/m²)", 1.0, 12.0, 3.0)
dead_load_factor = st.sidebar.slider("Dead Load Factor", 0.5, 3.0, 1.2)
mutation = st.sidebar.slider("Evolution Mutation Rate", 0.0, 1.0, 0.25)

# =========================================================
# EUROCODE-INSPIRED STRUCTURAL MODEL (SIMPLIFIED)
# =========================================================
def structural_model():
    area = width * depth

    material_strength = {
        "Concrete": 55,
        "Steel": 120,
        "Timber": 35,
        "Hybrid": 80
    }[material]

    importance_factor = {
        "Low": 0.9,
        "Normal": 1.0,
        "High": 1.2
    }[importance]

    dead_load = area * floors * dead_load_factor * importance_factor
    live_load_total = area * floors * live_load * importance_factor

    total_load = dead_load + live_load_total
    capacity = area * material_strength * 1.1

    utilization = total_load / capacity
    stability = max(0.0, 1.0 - utilization)

    return {
        "dead_load": dead_load,
        "live_load": live_load_total,
        "total_load": total_load,
        "capacity": capacity,
        "utilization": utilization,
        "stability": stability
    }

# =========================================================
# EVOLUTION FUNCTION
# =========================================================
def evolve(value, mutation_rate):
    drift = np.random.normal(0, mutation_rate)
    return float(np.clip(value + drift, 0, 1))

# =========================================================
# FLOORPLAN GENERATOR
# =========================================================
def generate_plan():
    symbols = ["■", "□", "▣", "▢"]
    return [
        [[random.choice(symbols) for _ in range(6)] for _ in range(6)]
        for _ in range(floors)
    ]

# =========================================================
# CONTROL PANEL (START / STOP LOOP)
# =========================================================
colA, colB = st.columns(2)

with colA:
    if st.button("🚀 Start Evolution Engine"):
        st.session_state.running = True

with colB:
    if st.button("🛑 Stop Engine"):
        st.session_state.running = False

# =========================================================
# CORE SIMULATION STEP
# =========================================================
def simulation_step():
    analysis = structural_model()

    # evolve stability
    st.session_state.stability = evolve(
        st.session_state.stability,
        mutation
    )

    # combine physical model + evolution drift
    st.session_state.stability = (st.session_state.stability + analysis["stability"]) / 2

    # history tracking
    st.session_state.history.append(st.session_state.stability)

    if len(st.session_state.history) > 50:
        st.session_state.history.pop(0)

    return analysis

analysis = structural_model()
floorplans = generate_plan()

# =========================================================
# DASHBOARD LAYOUT
# =========================================================
col1, col2, col3 = st.columns(3)

# -------------------------
# STRUCTURAL CORE
# -------------------------
with col1:
    st.subheader("📐 Structural Intelligence")

    st.metric("Total Load", f"{analysis['total_load']:.1f}")
    st.metric("Capacity", f"{analysis['capacity']:.1f}")
    st.metric("Utilization", f"{analysis['utilization']:.3f}")
    st.metric("Stability Index", f"{analysis['stability']:.3f}")

    if analysis["stability"] > 0.75:
        st.success("Stable structural regime")
    elif analysis["stability"] > 0.45:
        st.warning("Stress accumulation detected")
    else:
        st.error("Collapse risk zone")

# -------------------------
# FLOOR SYSTEM
# -------------------------
with col2:
    st.subheader("🏗️ Floor Geometry Field")

    for i, floor in enumerate(floorplans):
        st.text(f"Level {i+1}")
        for row in floor:
            st.text(" ".join(row))

# -------------------------
# EVOLUTION CORE
# -------------------------
with col3:
    st.subheader("🧬 Evolution Engine State")

    st.write("Current Stability")
    st.progress(st.session_state.stability)

    st.write("Environmental Stability (Eurocode-like)")
    st.progress(analysis["stability"])

    blended = (st.session_state.stability + analysis["stability"]) / 2
    st.write("System Harmony")
    st.progress(blended)

# =========================================================
# EVOLUTION LOOP EXECUTION
# =========================================================
if st.session_state.running:
    st.info("🧬 Evolution engine active... generating architectural mutations")

    analysis = simulation_step()
    st.session_state.tick += 1

    st.toast(f"Generation {st.session_state.tick} evolved")

    time.sleep(0.3)
    st.rerun()

# =========================================================
# HISTORY GRAPH
# =========================================================
st.divider()
st.subheader("📊 Stability Evolution Timeline")

fig, ax = plt.subplots()
ax.plot(st.session_state.history)
ax.set_title("Architectural Stability Drift")
ax.set_xlabel("Generations")
ax.set_ylabel("Stability")

st.pyplot(fig)

# =========================================================
# MANUAL RUN BUTTON (ONE-SHOT SIMULATION)
# =========================================================
st.divider()
st.subheader("🌍 Manual Simulation Step")

if st.button("Run Single Evolution Step"):
    analysis = simulation_step()
    st.success(f"Step complete — stability: {st.session_state.stability:.3f}")
