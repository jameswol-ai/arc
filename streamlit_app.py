# =========================================================
# RANDOM AI — REAL STRUCTURAL SOLVER + FLOORPLAN ENGINE v22
# Architecture → Floorplan → Structure → Deformation → Evolution
# =========================================================

import streamlit as st
import numpy as np
import random
import time
import matplotlib.pyplot as plt

st.set_page_config(page_title="Random AI Structural Solver v22", layout="wide")

st.title("🏗️ Random AI v22 — Structural Solver + Floorplan Engine")
st.caption("2D architecture with simplified physics-based deformation (spring-mass model)")

# =========================================================
# STATE
# =========================================================
if "running" not in st.session_state:
    st.session_state.running = False

if "history" not in st.session_state:
    st.session_state.history = []

if "tick" not in st.session_state:
    st.session_state.tick = 0

if "stability" not in st.session_state:
    st.session_state.stability = 0.7

# =========================================================
# INPUTS
# =========================================================
st.sidebar.header("Design Controls")

floors = st.sidebar.slider("Floors", 1, 50, 10)
width = st.sidebar.slider("Width (m)", 10, 80, 30)
depth = st.sidebar.slider("Depth (m)", 10, 80, 20)

density = st.sidebar.slider("Grid Density", 3, 10, 5)
load_factor = st.sidebar.slider("Load Factor", 1.0, 10.0, 3.0)
mutation = st.sidebar.slider("Evolution Rate", 0.0, 1.0, 0.2)

# =========================================================
# FLOORPLAN
# =========================================================
def generate_floorplan():
    return [
        [
            [random.choice([0, 1, 2, 3]) for _ in range(density)]
            for _ in range(density)
        ]
        for _ in range(min(floors, 15))
    ]

# =========================================================
# NODE GRID
# =========================================================
def build_nodes():
    nodes = []
    fixed = set()

    dx = width / density
    dy = depth / density

    for i in range(density):
        for j in range(density):
            nodes.append({
                "pos": np.array([i * dx, j * dy], dtype=float),
                "disp": np.array([0.0, 0.0], dtype=float),
                "force": np.array([0.0, 0.0], dtype=float)
            })

            if j == 0:
                fixed.add(len(nodes) - 1)

    return nodes, fixed

# =========================================================
# SPRINGS (STRUCTURAL BEAMS)
# =========================================================
def build_springs():
    springs = []

    for i in range(density):
        for j in range(density):
            idx = i * density + j

            if i < density - 1:
                springs.append((idx, idx + density))
            if j < density - 1:
                springs.append((idx, idx + 1))

    return springs

# =========================================================
# LOAD APPLICATION
# =========================================================
def apply_loads(nodes):
    for n in nodes:
        n["force"][:] = 0
        n["force"][1] -= load_factor

# =========================================================
# SPRING SOLVER (ITERATIVE RELAXATION)
# =========================================================
def solve(nodes, springs, fixed):
    k = 0.06

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
# STABILITY
# =========================================================
def compute_stability(nodes):
    total = 0

    for n in nodes:
        total += np.linalg.norm(n["disp"])

    avg = total / len(nodes)
    stability = 1.0 / (1.0 + avg)

    return stability, avg

# =========================================================
# EVOLUTION
# =========================================================
def evolve(current, target):
    noise = np.random.normal(0, mutation * 0.05)
    return float(np.clip(0.8 * current + 0.2 * target + noise, 0, 1))

# =========================================================
# SIMULATION STEP
# =========================================================
def step():
    nodes, fixed = build_nodes()
    springs = build_springs()

    apply_loads(nodes)
    nodes = solve(nodes, springs, fixed)

    stability, deformation = compute_stability(nodes)

    st.session_state.stability = evolve(
        st.session_state.stability,
        stability
    )

    st.session_state.history.append(st.session_state.stability)

    if len(st.session_state.history) > 80:
        st.session_state.history.pop(0)

    return nodes, springs, stability, deformation

# =========================================================
# INIT
# =========================================================
floorplan = generate_floorplan()
nodes, springs, stability, deformation = step()

# =========================================================
# CONTROLS
# =========================================================
c1, c2 = st.columns(2)

with c1:
    if st.button("🚀 Start Solver"):
        st.session_state.running = True

with c2:
    if st.button("⛔ Stop"):
        st.session_state.running = False

# =========================================================
# DEFORMATION VISUALIZATION
# =========================================================
st.subheader("🏗️ Structural Deformation Field")

fig, ax = plt.subplots()

for n in nodes:
    x, y = n["pos"]
    dx, dy = n["disp"]

    ax.plot(x, y, "bo")
    ax.plot(x + dx, y + dy, "ro")
    ax.plot([x, x + dx], [y, y + dy], "gray", alpha=0.5)

ax.set_title("Blue = original, Red = deformed")
st.pyplot(fig)

# =========================================================
# METRICS
# =========================================================
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Stability", f"{stability:.3f}")

with col2:
    st.metric("Avg Deformation", f"{deformation:.4f}")

with col3:
    st.progress(min(1.0, stability))

# =========================================================
# FLOORPLAN
# =========================================================
st.subheader("🏛️ Floorplan System")

for f in floorplan[:3]:
    for row in f:
        st.text(" ".join(str(x) for x in row))
    st.text("---")

# =========================================================
# LOOP
# =========================================================
if st.session_state.running:
    step()
    st.session_state.tick += 1
    st.toast(f"Step {st.session_state.tick}")
    time.sleep(0.25)
    st.rerun()

# =========================================================
# HISTORY
# =========================================================
st.divider()
st.subheader("📈 Stability History")

if len(st.session_state.history) > 2:
    fig, ax = plt.subplots()
    ax.plot(st.session_state.history)
    st.pyplot(fig)

# =========================================================
# MANUAL STEP
# =========================================================
st.divider()

if st.button("Run Single Step"):
    step()
    st.success("Simulation updated")
