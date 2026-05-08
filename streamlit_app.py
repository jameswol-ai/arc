=========================================================

🏗️ RANDOM AI v21 — FULL ARCHITECTURE + STRUCTURE + BIM PIPELINE

Architecture → Structure → MEP → Cost → Export → Evolution

Repo-Driven Modular Engineering System

=========================================================

import streamlit as st import numpy as np import random import time import matplotlib.pyplot as plt

-------------------------

OPTIONAL MODULE IMPORTS

(safe fallbacks for missing files)

-------------------------

try: from architecture.floorplan_engine import generate_floorplan from architecture.zoning_engine import zone_building from architecture.room_generator import generate_rooms except: generate_floorplan = None zone_building = None generate_rooms = None

try: from structure.grid_generator import generate_grid from structure.eurocode_engine import eurocode_check from structure.load_calculator import calculate_loads except: generate_grid = None eurocode_check = None calculate_loads = None

try: from rendering.massing_renderer import render_mass except: render_mass = None

=========================================================

APP CONFIG

=========================================================

st.set_page_config(page_title="Random AI v21", layout="wide")

st.title("🏗️ Random AI v21 — Architecture + Structural BIM Engine") st.caption("Architecture → Structure → Simulation → Evolution → Export Pipeline")

=========================================================

STATE

=========================================================

if "running" not in st.session_state: st.session_state.running = False

if "history" not in st.session_state: st.session_state.history = []

if "stability" not in st.session_state: st.session_state.stability = 0.75

if "tick" not in st.session_state: st.session_state.tick = 0

=========================================================

SIDEBAR INPUTS

=========================================================

st.sidebar.header("Design Controls")

floors = st.sidebar.slider("Floors", 1, 100, 15) span = st.sidebar.slider("Grid Span (m)", 2, 12, 4) width = st.sidebar.slider("Width (m)", 10, 150, 50) depth = st.sidebar.slider("Depth (m)", 10, 150, 40)

material = st.sidebar.selectbox("Material", ["Concrete", "Steel", "Hybrid"]) wind = st.sidebar.slider("Wind Load", 0.0, 1.0, 0.35) mutation = st.sidebar.slider("Evolution Rate", 0.0, 1.0, 0.25)

=========================================================

ARCHITECTURE ENGINE (HIGH LEVEL)

=========================================================

def architecture_engine(): if generate_floorplan: return generate_floorplan(width, depth, floors)

return {
    "layout": "procedural-grid",
    "rooms": int((width * depth) / 20),
    "cores": max(1, floors // 10)
}

=========================================================

STRUCTURAL ENGINE

=========================================================

def structural_engine():

area = width * depth

strength_map = {
    "Concrete": 65,
    "Steel": 120,
    "Hybrid": 95
}

strength = strength_map[material]

gravity_load = area * floors * 4.8
wind_load = gravity_load * wind * (floors / 10)

total_load = gravity_load + wind_load
capacity = area * strength

utilization = total_load / max(capacity, 1e-6)
stability = max(0.0, 1.0 - utilization)

return {
    "load": total_load,
    "capacity": capacity,
    "utilization": utilization,
    "stability": stability
}

=========================================================

GRID + STRUCTURE LAYOUT

=========================================================

def structural_grid():

grid_x = max(2, int(width / span))
grid_y = max(2, int(depth / span))

return {
    "grid": (grid_x, grid_y),
    "columns": grid_x * grid_y,
    "beams": (grid_x - 1) * grid_y + (grid_y - 1) * grid_x,
    "nodes": [(i, j) for i in range(grid_x) for j in range(grid_y)]
}

=========================================================

LOAD FLOW + EUROCODE CHECK (SIMPLIFIED)

=========================================================

def load_system(struct):

base = structural_engine()

column_count = struct["columns"]

load_per_column = base["load"] / max(column_count, 1)

stress = load_per_column / max(base["capacity"] / 10, 1e-6)

euro_ok = stress < 1.0

return {
    "column_load": load_per_column,
    "stress": stress,
    "eurocode_pass": euro_ok
}

=========================================================

EVOLUTION SYSTEM

=========================================================

def evolve(current, target): noise = np.random.normal(0, mutation * 0.05) return float(np.clip(0.8 * current + 0.2 * target + noise, 0, 1))

=========================================================

SIMULATION STEP

=========================================================

def step():

analysis = structural_engine()

st.session_state.stability = evolve(
    st.session_state.stability,
    analysis["stability"]
)

st.session_state.history.append(st.session_state.stability)

if len(st.session_state.history) > 120:
    st.session_state.history.pop(0)

return analysis

=========================================================

PIPELINE EXECUTION

=========================================================

architecture = architecture_engine() structure = structural_grid() analysis = structural_engine() loads = load_system(structure)

=========================================================

CONTROLS

=========================================================

col1, col2 = st.columns(2)

with col1: if st.button("🚀 Start Full BIM Simulation"): st.session_state.running = True

with col2: if st.button("⛔ Stop"): st.session_state.running = False

=========================================================

DASHBOARD

=========================================================

A, B, C = st.columns(3)

-------------------------

ARCHITECTURE

-------------------------

with A: st.subheader("🏛️ Architecture")

st.write("Rooms:", architecture.get("rooms", "N/A"))
st.write("Core Systems:", architecture.get("cores", "N/A"))

-------------------------

STRUCTURE

-------------------------

with B: st.subheader("🏗️ Structure")

st.metric("Load", f"{analysis['load']:.1f}")
st.metric("Capacity", f"{analysis['capacity']:.1f}")
st.metric("Utilization", f"{analysis['utilization']:.3f}")
st.metric("Stability", f"{analysis['stability']:.3f}")

if analysis["stability"] > 0.75:
    st.success("Stable structure")
elif analysis["stability"] > 0.4:
    st.warning("Stress detected")
else:
    st.error("Failure risk")

-------------------------

LOAD + EUROCODE

-------------------------

with C: st.subheader("📐 Eurocode Check")

st.metric("Column Load", f"{loads['column_load']:.2f}")
st.metric("Stress", f"{loads['stress']:.2f}")

if loads["eurocode_pass"]:
    st.success("Eurocode PASS")
else:
    st.error("Eurocode FAIL")

st.progress(min(1.0, loads["stress"]))

=========================================================

LOOP ENGINE

=========================================================

if st.session_state.running: step() st.session_state.tick += 1 st.toast(f"Cycle {st.session_state.tick}") time.sleep(0.2) st.rerun()

=========================================================

EVOLUTION HISTORY

=========================================================

st.divider() st.subheader("📈 Structural Evolution")

if len(st.session_state.history) > 2: fig, ax = plt.subplots() ax.plot(st.session_state.history) ax.set_title("Stability Evolution") st.pyplot(fig)

=========================================================

SINGLE STEP

=========================================================

st.divider()

if st.button("Run Single Simulation Step"): step() st.success(f"Stability: {st.session_state.stability:.3f}")

=========================================================

REPO ARCHITECTURE VIEW

=========================================================

st.divider() st.subheader("📦 System Architecture")

st.code(""" random/ │ ├── streamlit_app.py ├── architecture/ ├── structure/ ├── mep/ ├── gis/ ├── rendering/ ├── export/ ├── cost/ ├── standards/ └── ai/

Pipeline: Architecture → Structure → Load → Eurocode → Evolution → Export """)
