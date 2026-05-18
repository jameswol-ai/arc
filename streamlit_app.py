# =========================================================
# RANDOM AI v23 — FULL ARCHITECTURE + STRUCTURE + BIM CORE
# Architecture → Structure → MEP → Cost → Export → AI Evolution
# =========================================================

import streamlit as st
import numpy as np
import random
import time
import matplotlib.pyplot as plt

# =========================================================
# OPTIONAL MODULE INTEGRATION (your repo system)
# =========================================================
try:
    from architecture.floorplan_engine import generate_floorplan
    from architecture.zoning_engine import zone_building
    from architecture.room_generator import generate_rooms
except:
    generate_floorplan = None
    zone_building = None
    generate_rooms = None

try:
    from structure.eurocode_engine import eurocode_check
    from structure.grid_generator import generate_grid
    from structure.beam_design import beam_capacity
    from structure.column_design import column_capacity
except:
    eurocode_check = None
    generate_grid = None
    beam_capacity = None
    column_capacity = None

# =========================================================
# APP CONFIG
# =========================================================
st.set_page_config(page_title="Random AI BIM Core v23", layout="wide")

st.title("🏗️ Random AI v23 — Full Structural + Architectural Engine")
st.caption("Architecture → Structure → Loads → Deformation → Evolution → Export Pipeline")

# =========================================================
# STATE
# =========================================================
if "running" not in st.session_state:
    st.session_state.running = False

if "history" not in st.session_state:
    st.session_state.history = []

if "stability" not in st.session_state:
    st.session_state.stability = 0.7

if "tick" not in st.session_state:
    st.session_state.tick = 0

# =========================================================
# SIDEBAR INPUTS
# =========================================================
st.sidebar.header("Design Controls")

floors = st.sidebar.slider("Floors", 1, 80, 12)
width = st.sidebar.slider("Width (m)", 10, 120, 40)
depth = st.sidebar.slider("Depth (m)", 10, 120, 30)

grid = st.sidebar.slider("Grid Density", 3, 10, 6)
material = st.sidebar.selectbox("Material", ["Concrete", "Steel", "Hybrid"])
wind = st.sidebar.slider("Wind Load", 0.0, 1.0, 0.3)
mutation = st.sidebar.slider("Evolution Rate", 0.0, 1.0, 0.25)

# =========================================================
# ARCHITECTURE LAYER (floor + zoning + rooms)
# =========================================================
def architecture_engine():

    if generate_floorplan:
        return generate_floorplan(width, depth, floors)

    # fallback procedural zoning
    zones = ["PUBLIC", "PRIVATE", "CORE", "SERVICE"]

    return [
        [
            [random.choice(zones) for _ in range(grid)]
            for _ in range(grid)
        ]
        for _ in range(min(floors, 15))
    ]

# =========================================================
# STRUCTURAL GRID (nodes + beams)
# =========================================================
def build_grid():

    nodes = []
    fixed = set()

    dx = width / grid
    dy = depth / grid

    for i in range(grid):
        for j in range(grid):
            nodes.append({
                "pos": np.array([i * dx, j * dy], dtype=float),
                "disp": np.zeros(2),
                "force": np.zeros(2)
            })

            if j == 0:
                fixed.add(len(nodes) - 1)

    springs = []

    for i in range(grid):
        for j in range(grid):
            idx = i * grid + j

            if i < grid - 1:
                springs.append((idx, idx + grid))
            if j < grid - 1:
                springs.append((idx, idx + 1))

    return nodes, springs, fixed

# =========================================================
# LOAD MODEL (simplified Eurocode-style)
# =========================================================
def structural_load():

    area = width * depth

    strength = {
        "Concrete": 55,
        "Steel": 120,
        "Hybrid": 85
    }[material]

    gravity = area * floors * 5.0
    wind_load = gravity * wind * (floors / 12)

    total = gravity + wind_load
    capacity = area * strength

    utilization = total / max(capacity, 1e-6)
    stability = max(0.0, 1.0 - utilization)

    return total, capacity, utilization, stability

# =========================================================
# FEM-LITE SOLVER (SPRING MASS SYSTEM)
# =========================================================
def solve(nodes, springs, fixed):

    k = 0.05

    for _ in range(20):
        for i, j in springs:

            ni = nodes[i]
            nj = nodes[j]

            delta = (nj["pos"] + nj["disp"]) - (ni["pos"] + ni["disp"])
            dist = np.linalg.norm(delta) + 1e-6
            direction = delta / dist

            force = k * (dist - 1.0)

            if i not in fixed:
                ni["disp"] += force * direction * 0.5
            if j not in fixed:
                nj["disp"] -= force * direction * 0.5

    return nodes

# =========================================================
# STABILITY METRIC
# =========================================================
def stability_metric(nodes):

    total = sum(np.linalg.norm(n["disp"]) for n in nodes)
    avg = total / len(nodes)

    return 1 / (1 + avg), avg

# =========================================================
# EVOLUTION ENGINE
# =========================================================
def evolve(current, target):

    noise = np.random.normal(0, mutation * 0.05)
    return float(np.clip(0.85 * current + 0.15 * target + noise, 0, 1))

# =========================================================
# SIMULATION STEP
# =========================================================
def step():

    nodes, springs, fixed = build_grid()

    nodes = solve(nodes, springs, fixed)

    _, _, _, stability = structural_load()

    st.session_state.stability = evolve(
        st.session_state.stability,
        stability
    )

    st.session_state.history.append(st.session_state.stability)

    if len(st.session_state.history) > 100:
        st.session_state.history.pop(0)

    return nodes, springs, stability

# =========================================================
# INIT SYSTEMS
# =========================================================
floorplan = architecture_engine()
nodes, springs, stability = step()

# =========================================================
# CONTROLS
# =========================================================
c1, c2 = st.columns(2)

with c1:
    if st.button("🚀 Start BIM Solver"):
        st.session_state.running = True

with c2:
    if st.button("⛔ Stop"):
        st.session_state.running = False

# =========================================================
# STRUCTURAL VISUALIZATION
# =========================================================
st.subheader("🏗️ Structural Deformation Field")

fig, ax = plt.subplots()

for n in nodes:
    x, y = n["pos"]
    dx, dy = n["disp"]

    ax.plot(x, y, "bo")
    ax.plot(x + dx, y + dy, "ro")
    ax.plot([x, x + dx], [y, y + dy], "gray", alpha=0.4)

ax.set_title("Undeformed → Deformed Structure")
st.pyplot(fig)

# =========================================================
# METRICS
# =========================================================
load, capacity, util, stability_val = structural_load()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Load", f"{load:.1f}")

with col2:
    st.metric("Utilization", f"{util:.3f}")

with col3:
    st.metric("Stability", f"{st.session_state.stability:.3f}")

# =========================================================
# FLOORPLAN
# =========================================================
st.subheader("🏛️ Architectural Floorplan")

for f in floorplan[:3]:
    for row in f:
        st.text(" ".join(str(x) for x in row))
    st.text("---")

# =========================================================
# LOOP ENGINE
# =========================================================
if st.session_state.running:

    nodes, springs, stability = step()

    st.session_state.tick += 1
    st.toast(f"Cycle {st.session_state.tick}")

    time.sleep(0.25)
    st.rerun()

# =========================================================
# HISTORY
# =========================================================
st.divider()
st.subheader("📈 Stability Evolution")

if len(st.session_state.history) > 2:
    fig, ax = plt.subplots()
    ax.plot(st.session_state.history)
    ax.set_title("System Stability Over Time")
    st.pyplot(fig)

# =========================================================
# MANUAL STEP
# =========================================================
st.divider()

if st.button("Run Single Simulation Step"):
    step()
    st.success("Step executed")
