# streamlit_app.py
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
st.caption("A living design system inspired by structural logic, evolution, and Eurocode-style constraints")

# =========================================================
# SIDEBAR PARAMETERS
# =========================================================
st.sidebar.header("Building Configuration")

floors = st.sidebar.slider("Floors", 1, 60, 8)
width = st.sidebar.slider("Width (m)", 5, 120, 25)
depth = st.sidebar.slider("Depth (m)", 5, 120, 18)

material = st.sidebar.selectbox("Material", ["Concrete", "Steel", "Timber", "Hybrid"])
importance = st.sidebar.selectbox("Importance Class (Eurocode-like)", ["Low", "Normal", "High"])

live_load = st.sidebar.slider("Live Load (kN/m²)", 1.0, 12.0, 3.0)
dead_load_factor = st.sidebar.slider("Dead Load Factor", 0.5, 3.0, 1.2)

mutation = st.sidebar.slider("Evolution Mutation Rate", 0.0, 1.0, 0.25)

# =========================================================
# EUROCODE-INSPIRED LOAD MODEL (SIMPLIFIED)
# =========================================================
def structural_model(floors, width, depth, live_load, dead_load_factor, material, importance):
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
        "area": area,
        "dead_load": dead_load,
        "live_load": live_load_total,
        "total_load": total_load,
        "capacity": capacity,
        "utilization": utilization,
        "stability": stability
    }

analysis = structural_model(
    floors, width, depth, live_load,
    dead_load_factor, material, importance
)

# =========================================================
# DESIGN GENOME (EVOLUTION SYSTEM)
# =========================================================
def evolve(score, mutation):
    drift = np.random.normal(0, mutation)
    return float(np.clip(score + drift, 0, 1))

# =========================================================
# FLOORPLAN GENERATOR (GRID-BASED)
# =========================================================
def generate_plan(floors):
    symbols = ["■", "□", "▣", "▢"]
    return [
        [[random.choice(symbols) for _ in range(6)] for _ in range(6)]
        for _ in range(floors)
    ]

floorplans = generate_plan(floors)

# =========================================================
# STRUCTURAL PERFORMANCE HISTORY
# =========================================================
history = [evolve(analysis["stability"], mutation) for _ in range(12)]

# =========================================================
# DASHBOARD LAYOUT
# =========================================================
col1, col2, col3 = st.columns(3)

# -------------------------
# COLUMN 1 — STRUCTURAL CORE
# -------------------------
with col1:
    st.subheader("📐 Structural Intelligence")

    st.metric("Total Load", f"{analysis['total_load']:.1f}")
    st.metric("Capacity", f"{analysis['capacity']:.1f}")
    st.metric("Utilization", f"{analysis['utilization']:.3f}")
    st.metric("Stability Index", f"{analysis['stability']:.3f}")

    if analysis["stability"] > 0.75:
        st.success("Structurally efficient system")
    elif analysis["stability"] > 0.45:
        st.warning("Moderate structural stress detected")
    else:
        st.error("Critical instability zone")

# -------------------------
# COLUMN 2 — FLOORPLANS
# -------------------------
with col2:
    st.subheader("🏗️ Floor System Map")

    for i, floor in enumerate(floorplans):
        st.text(f"Level {i+1}")
        for row in floor:
            st.text(" ".join(row))

# -------------------------
# COLUMN 3 — EVOLUTION ENGINE
# -------------------------
with col3:
    st.subheader("🧬 Design Evolution Field")

    current = analysis["stability"]
    evolved = evolve(current, mutation)

    st.write("Base Stability")
    st.progress(current)

    st.write("Evolved Stability")
    st.progress(evolved)

    if evolved > current:
        st.success("Evolution improved structural harmony")
    else:
        st.info("Mutation introduced instability, exploring new geometry")

# =========================================================
# GRAPHICAL ANALYSIS LAYER
# =========================================================
st.divider()
st.subheader("📊 Structural Evolution Graph")

fig, ax = plt.subplots()

ax.plot(history)
ax.set_title("Stability Evolution Over Iterations")
ax.set_xlabel("Iteration")
ax.set_ylabel("Stability Index")

st.pyplot(fig)

# =========================================================
# LOAD BREAKDOWN VISUALIZATION
# =========================================================
st.subheader("⚖️ Load Composition")

fig2, ax2 = plt.subplots()

labels = ["Dead Load", "Live Load"]
values = [analysis["dead_load"], analysis["live_load"]]

ax2.bar(labels, values)

ax2.set_title("Load Distribution (Simplified Eurocode Model)")

st.pyplot(fig2)

# =========================================================
# SIMULATION ENGINE
# =========================================================
st.divider()
st.subheader("🌍 Living Architecture Simulation")

if st.button("Run Evolution Cycle"):
    st.write("Running structural evolution cycle...")

    progress = st.progress(0)
    score = analysis["stability"]

    for i in range(10):
        time.sleep(0.2)
        score = evolve(score, mutation)
        progress.progress((i + 1) * 10)

    st.metric("Final Evolved Stability", f"{score:.3f}")

    if score > 0.8:
        st.success("Highly stable architectural organism formed 🧬🏗️")
    elif score > 0.5:
        st.warning("Adaptive structure achieved with moderate resilience")
    else:
        st.error("System drifted into structural collapse regime")
