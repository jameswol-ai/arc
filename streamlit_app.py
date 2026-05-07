import streamlit as st
import random
import math
import time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# =========================================================
# 🏗️ RANDOM AI — MULTI-FLOOR PROCEDURAL BUILDING ENGINE v19
# =========================================================

st.set_page_config(
    page_title="Random AI Procedural Building Engine",
    layout="wide"
)

st.title("🏗️ Random AI v19 — Procedural Building Intelligence")
st.caption(
    "Autonomous architecture + Eurocode-inspired structural evolution"
)

# =========================================================
# SESSION STATE
# =========================================================

if "running" not in st.session_state:
    st.session_state.running = False

if "history" not in st.session_state:
    st.session_state.history = []

if "tick" not in st.session_state:
    st.session_state.tick = 0

if "stability" not in st.session_state:
    st.session_state.stability = 0.75


# =========================================================
# SIDEBAR — BUILDING PARAMETERS
# =========================================================

st.sidebar.header("🏢 Building Parameters")

building_type = st.sidebar.selectbox(
    "Building Type",
    [
        "Residential Tower",
        "Office",
        "Mixed Use",
        "Hotel",
        "Hospital"
    ]
)

floors = st.sidebar.slider("Floors", 1, 60, 12)
width = st.sidebar.slider("Site Width (m)", 20, 120, 40)
depth = st.sidebar.slider("Site Depth (m)", 20, 120, 60)

grid_spacing = st.sidebar.slider("Structural Grid (m)", 4, 10, 6)

material = st.sidebar.selectbox(
    "Primary Material",
    ["Concrete", "Steel", "Timber", "Hybrid"]
)

facade_style = st.sidebar.selectbox(
    "Facade Style",
    [
        "Glass Curtain Wall",
        "Brutalist Concrete",
        "Parametric Fins",
        "Green Facade"
    ]
)

core_position = st.sidebar.selectbox(
    "Core Position",
    ["Center", "Edge", "Dual Core"]
)

mutation = st.sidebar.slider("Mutation Rate", 0.0, 1.0, 0.2)

env_stress = st.sidebar.slider(
    "Environmental Stress",
    0.0,
    1.0,
    0.35
)

floor_height = st.sidebar.slider("Floor Height (m)", 3.0, 5.0, 3.5)

live_load = st.sidebar.slider("Live Load kN/m²", 1.0, 10.0, 3.0)

dead_load_factor = st.sidebar.slider(
    "Dead Load Factor",
    0.5,
    3.0,
    1.2
)

# =========================================================
# MATERIAL DATABASE
# =========================================================

strength_map = {
    "Concrete": 55,
    "Steel": 120,
    "Timber": 35,
    "Hybrid": 85
}

# =========================================================
# STRUCTURAL GRID GENERATOR
# =========================================================

def generate_grid():
    cols = []

    x_count = int(width / grid_spacing)
    y_count = int(depth / grid_spacing)

    for x in range(x_count + 1):
        for y in range(y_count + 1):
            cols.append(
                (
                    x * grid_spacing,
                    y * grid_spacing
                )
            )

    return cols


# =========================================================
# CORE GENERATOR
# =========================================================

def generate_core():
    if core_position == "Center":
        return {
            "x": width * 0.4,
            "y": depth * 0.4,
            "w": width * 0.2,
            "h": depth * 0.2
        }

    elif core_position == "Edge":
        return {
            "x": width * 0.05,
            "y": depth * 0.35,
            "w": width * 0.18,
            "h": depth * 0.3
        }

    else:
        return {
            "x": width * 0.2,
            "y": depth * 0.35,
            "w": width * 0.15,
            "h": depth * 0.25
        }


# =========================================================
# PROCEDURAL ROOM GENERATOR
# =========================================================

def generate_floor_rooms(level):

    rooms = []

    # Different program zones
    if level == 0:
        room_types = [
            "Lobby",
            "Retail",
            "Cafe",
            "Reception"
        ]

    elif level <= 3:
        room_types = [
            "Parking",
            "Storage",
            "Mechanical"
        ]

    else:
        if building_type == "Residential Tower":
            room_types = [
                "Apartment",
                "Apartment",
                "Corridor",
                "Utility"
            ]
        else:
            room_types = [
                "Office",
                "Meeting",
                "Breakout",
                "Corridor"
            ]

    room_count = random.randint(6, 14)

    for _ in range(room_count):

        rw = random.uniform(4, 10)
        rh = random.uniform(4, 10)

        rx = random.uniform(0, width - rw)
        ry = random.uniform(0, depth - rh)

        rooms.append({
            "x": rx,
            "y": ry,
            "w": rw,
            "h": rh,
            "type": random.choice(room_types)
        })

    return rooms


# =========================================================
# STRUCTURAL ANALYSIS
# =========================================================

def structural_analysis():

    area = width * depth

    total_area = area * floors

    strength = strength_map[material]

    dead_load = total_area * dead_load_factor
    imposed_load = total_area * live_load

    wind_penalty = imposed_load * env_stress * 0.15

    total_load = dead_load + imposed_load + wind_penalty

    capacity = area * strength * 1.1

    utilization = total_load / capacity

    stability = max(0.0, 1.0 - utilization)

    drift = utilization * floors * 0.003

    return {
        "total_load": total_load,
        "capacity": capacity,
        "utilization": utilization,
        "stability": stability,
        "drift": drift
    }


# =========================================================
# EVOLUTION ENGINE
# =========================================================

def evolve(current, target, mutation_rate):

    noise = np.random.normal(0, mutation_rate * 0.08)

    blended = (
        0.88 * current
        + 0.12 * target
        + noise
    )

    return float(np.clip(blended, 0, 1))


# =========================================================
# FLOORPLAN DRAWER
# =========================================================

def draw_floor(level):

    rooms = generate_floor_rooms(level)
    core = generate_core()
    grid = generate_grid()

    fig, ax = plt.subplots(figsize=(8, 8))

    # Building boundary
    ax.add_patch(
        Rectangle(
            (0, 0),
            width,
            depth,
            fill=False,
            linewidth=3
        )
    )

    # Structural columns
    for col in grid:
        ax.plot(col[0], col[1], "ks", markersize=4)

    # Core
    ax.add_patch(
        Rectangle(
            (core["x"], core["y"]),
            core["w"],
            core["h"],
            fill=True,
            alpha=0.3
        )
    )

    # Rooms
    for room in rooms:

        ax.add_patch(
            Rectangle(
                (room["x"], room["y"]),
                room["w"],
                room["h"],
                fill=False
            )
        )

        ax.text(
            room["x"] + room["w"] / 2,
            room["y"] + room["h"] / 2,
            room["type"],
            fontsize=6,
            ha="center"
        )

    ax.set_xlim(0, width)
    ax.set_ylim(0, depth)

    ax.set_title(f"Level {level + 1}")

    ax.set_aspect("equal")

    return fig


# =========================================================
# MASSING GENERATOR
# =========================================================

def draw_massing():

    fig = plt.figure(figsize=(7, 7))
    ax = fig.add_subplot(111, projection='3d')

    for i in range(floors):

        z = i * floor_height

        ax.bar3d(
            0,
            0,
            z,
            width,
            depth,
            floor_height,
            shade=True,
            alpha=0.4
        )

    ax.set_title("Procedural Building Massing")

    ax.set_xlabel("Width")
    ax.set_ylabel("Depth")
    ax.set_zlabel("Height")

    return fig


# =========================================================
# SIMULATION STEP
# =========================================================

def simulation_step():

    analysis = structural_analysis()

    st.session_state.stability = evolve(
        st.session_state.stability,
        analysis["stability"],
        mutation
    )

    st.session_state.history.append(
        st.session_state.stability
    )

    if len(st.session_state.history) > 100:
        st.session_state.history.pop(0)

    return analysis


analysis = structural_analysis()

# =========================================================
# CONTROLS
# =========================================================

colA, colB = st.columns(2)

with colA:
    if st.button("🚀 Start Evolution"):
        st.session_state.running = True

with colB:
    if st.button("🛑 Stop Evolution"):
        st.session_state.running = False

# =========================================================
# MAIN TABS
# =========================================================

tabs = st.tabs([
    "🏗️ Floor Plans",
    "📐 Structural Analysis",
    "🌆 3D Massing",
    "🧬 Evolution",
    "🎨 Facade Intelligence"
])

# =========================================================
# FLOOR PLANS TAB
# =========================================================

with tabs[0]:

    st.subheader("Procedural Multi-Floor Layouts")

    level = st.slider(
        "Select Floor",
        1,
        floors,
        1
    )

    fig = draw_floor(level - 1)

    st.pyplot(fig)

# =========================================================
# STRUCTURAL ANALYSIS TAB
# =========================================================

with tabs[1]:

    st.subheader("Eurocode-Inspired Structural Metrics")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Total Load",
            f"{analysis['total_load']:.1f}"
        )

        st.metric(
            "Capacity",
            f"{analysis['capacity']:.1f}"
        )

    with c2:
        st.metric(
            "Utilization",
            f"{analysis['utilization']:.3f}"
        )

        st.metric(
            "Stability",
            f"{analysis['stability']:.3f}"
        )

    with c3:
        st.metric(
            "Lateral Drift",
            f"{analysis['drift']:.4f}"
        )

        st.metric(
            "Height",
            f"{floors * floor_height:.1f} m"
        )

    if analysis["stability"] > 0.75:
        st.success("Stable structural regime")

    elif analysis["stability"] > 0.45:
        st.warning("Moderate structural stress")

    else:
        st.error("Critical instability")

# =========================================================
# 3D MASSING TAB
# =========================================================

with tabs[2]:

    st.subheader("3D Procedural Massing")

    fig3d = draw_massing()

    st.pyplot(fig3d)

# =========================================================
# EVOLUTION TAB
# =========================================================

with tabs[3]:

    st.subheader("Evolution Intelligence")

    st.progress(st.session_state.stability)

    fig, ax = plt.subplots()

    ax.plot(st.session_state.history)

    ax.set_title("Structural Evolution")

    ax.set_xlabel("Generations")

    ax.set_ylabel("Stability")

    st.pyplot(fig)

# =========================================================
# FACADE TAB
# =========================================================

with tabs[4]:

    st.subheader("Facade Intelligence")

    st.write(f"Selected Style: {facade_style}")

    if facade_style == "Glass Curtain Wall":
        st.info(
            "High daylight penetration with elevated solar gain."
        )

    elif facade_style == "Brutalist Concrete":
        st.info(
            "Massive thermal stability and structural expression."
        )

    elif facade_style == "Parametric Fins":
        st.info(
            "Adaptive solar shading with rhythmic geometry."
        )

    else:
        st.info(
            "Vegetated facade system improving thermal behavior."
        )

# =========================================================
# EVOLUTION LOOP
# =========================================================

if st.session_state.running:

    st.info(
        "🧬 Autonomous architectural evolution running..."
    )

    simulation_step()

    st.session_state.tick += 1

    st.toast(
        f"Generation {st.session_state.tick}"
    )

    time.sleep(0.25)

    st.rerun()

# =========================================================
# MANUAL EVOLUTION STEP
# =========================================================

st.divider()

if st.button("⚡ Run Single Evolution Step"):

    simulation_step()

    st.success(
        f"Generation complete | Stability: "
        f"{st.session_state.stability:.3f}"
)
