# streamlit_app.py

import streamlit as st
import random
import math
import time
import json
from datetime import datetime

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# =========================================================
# 🏙️ RANDOM AI
# Autonomous Architecture + Structural Intelligence System
# Eurocode Inspired Simulation Engine
# =========================================================

st.set_page_config(
    page_title="Random Autonomous AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# SESSION STATE
# =========================================================

def init_state():
    defaults = {
        "cycle": 0,
        "history": [],
        "city_memory": [],
        "autonomous_mode": False,
        "population": [],
        "thoughts": [],
        "alerts": [],
        "design_score": 0,
        "structural_score": 0,
        "energy_score": 0,
        "evolution_score": 0,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_state()

# =========================================================
# UI HEADER
# =========================================================

st.title("🏙️ RANDOM AI")
st.caption(
    "Autonomous Architectural + Structural Intelligence Engine"
)

# =========================================================
# SIDEBAR CONTROLS
# =========================================================

st.sidebar.title("⚙️ RANDOM CONTROL CORE")

building_type = st.sidebar.selectbox(
    "Building Type",
    [
        "Residential Tower",
        "Office Building",
        "Hospital",
        "School",
        "Mixed Use",
        "Industrial Facility"
    ]
)

floors = st.sidebar.slider("Floors", 1, 100, 20)
span = st.sidebar.slider("Structural Span (m)", 3, 20, 8)
wind_load = st.sidebar.slider("Wind Load", 0.5, 5.0, 1.5)
seismic_factor = st.sidebar.slider("Seismic Factor", 0.1, 3.0, 1.0)
occupancy = st.sidebar.slider("Occupancy", 10, 10000, 500)

material = st.sidebar.selectbox(
    "Primary Material",
    ["Concrete", "Steel", "Timber", "Composite"]
)

st.sidebar.markdown("---")

run_cycle = st.sidebar.button("▶ Run Evolution Cycle")
autonomous = st.sidebar.toggle("🤖 Autonomous Mode")

# =========================================================
# DESIGN DNA ENGINE
# =========================================================

class DesignDNA:
    def __init__(self, floors, span, material):
        self.floors = floors
        self.span = span
        self.material = material

    def generate_geometry(self):
        width = random.randint(20, 80)
        depth = random.randint(20, 80)
        height = self.floors * random.uniform(3.0, 4.5)

        efficiency = random.uniform(0.5, 1.0)

        return {
            "width": width,
            "depth": depth,
            "height": round(height, 2),
            "efficiency": round(efficiency, 2)
        }

    def generate_floorplan(self):
        rooms = []

        room_types = [
            "Office",
            "Meeting Room",
            "Apartment",
            "Core",
            "Hall",
            "Laboratory",
            "Ward",
            "Studio"
        ]

        for _ in range(random.randint(5, 20)):
            rooms.append({
                "type": random.choice(room_types),
                "area": round(random.uniform(15, 120), 1)
            })

        return rooms

# =========================================================
# EUROCODE STRUCTURAL ENGINE
# =========================================================

class EurocodeEngine:

    def __init__(self, floors, span, wind, seismic, material):
        self.floors = floors
        self.span = span
        self.wind = wind
        self.seismic = seismic
        self.material = material

    def dead_load(self):
        return round(3.0 + self.floors * 0.15, 2)

    def live_load(self):
        return round(random.uniform(2.0, 5.0), 2)

    def wind_effect(self):
        return round(self.wind * self.floors * 0.8, 2)

    def seismic_effect(self):
        return round(self.seismic * self.floors * 0.6, 2)

    def beam_depth(self):
        depth = self.span * 1000 / 18
        return round(depth, 1)

    def column_size(self):
        size = 300 + self.floors * 8
        return round(size, 1)

    def utilization_ratio(self):
        ratio = random.uniform(0.45, 1.15)
        return round(ratio, 2)

    def compliance(self):
        ratio = self.utilization_ratio()

        if ratio <= 1.0:
            return "PASS", ratio
        return "FAIL", ratio

# =========================================================
# ENERGY + ENVIRONMENT ENGINE
# =========================================================

class SustainabilityEngine:

    def score(self):
        return round(random.uniform(40, 100), 1)

    def carbon(self):
        return round(random.uniform(100, 1500), 2)

    def daylight(self):
        return round(random.uniform(40, 95), 1)

    def ventilation(self):
        return round(random.uniform(30, 100), 1)

# =========================================================
# AI BRAIN
# =========================================================

class RandomBrain:

    def think(self):

        thoughts = [
            "Optimizing structural grid for lower bending moments.",
            "Reducing façade heat gain through adaptive shading.",
            "Exploring organic circulation geometry.",
            "Balancing occupant comfort with structural efficiency.",
            "Increasing daylight penetration into central core.",
            "Adjusting beam-column hierarchy.",
            "Re-evaluating lateral stability strategy.",
            "Analyzing wind vortex behavior around tower massing.",
            "Improving evacuation flow logic.",
            "Generating evolutionary geometry mutations."
        ]

        thought = random.choice(thoughts)
        st.session_state.thoughts.append(thought)

        return thought

    def evolve(self):

        evolution = random.uniform(0.0, 10.0)

        st.session_state.evolution_score += evolution

        return round(evolution, 2)

# =========================================================
# VISUALIZATION ENGINE
# =========================================================

class VisualizationEngine:

    @staticmethod
    def massing_plot(width, depth, height):

        fig = plt.figure(figsize=(6, 5))
        ax = fig.add_subplot(111, projection='3d')

        x = [0, width, width, 0, 0]
        y = [0, 0, depth, depth, 0]
        z = [0, 0, 0, 0, 0]

        ax.plot(x, y, z)
        ax.plot(x, y, [height]*5)

        for i in range(4):
            ax.plot(
                [x[i], x[i]],
                [y[i], y[i]],
                [0, height]
            )

        ax.set_title("Autonomous Building Massing")
        ax.set_xlabel("Width")
        ax.set_ylabel("Depth")
        ax.set_zlabel("Height")

        return fig

    @staticmethod
    def structural_chart(dead, live, wind, seismic):

        fig, ax = plt.subplots(figsize=(6, 4))

        labels = ["Dead", "Live", "Wind", "Seismic"]
        values = [dead, live, wind, seismic]

        ax.bar(labels, values)
        ax.set_title("Load Distribution")
        ax.set_ylabel("kN/m²")

        return fig

    @staticmethod
    def evolution_chart(history):

        fig, ax = plt.subplots(figsize=(7, 4))

        ax.plot(history)
        ax.set_title("AI Evolution Curve")
        ax.set_xlabel("Cycle")
        ax.set_ylabel("Evolution Score")

        return fig

# =========================================================
# MAIN SIMULATION ENGINE
# =========================================================


def run_simulation_cycle():

    dna = DesignDNA(floors, span, material)
    structure = EurocodeEngine(
        floors,
        span,
        wind_load,
        seismic_factor,
        material
    )

    sustainability = SustainabilityEngine()
    brain = RandomBrain()

    geometry = dna.generate_geometry()
    floorplan = dna.generate_floorplan()

    dead = structure.dead_load()
    live = structure.live_load()
    wind = structure.wind_effect()
    seismic = structure.seismic_effect()

    beam = structure.beam_depth()
    column = structure.column_size()

    compliance, ratio = structure.compliance()

    energy = sustainability.score()
    carbon = sustainability.carbon()
    daylight = sustainability.daylight()
    ventilation = sustainability.ventilation()

    thought = brain.think()
    evolution = brain.evolve()

    st.session_state.cycle += 1

    result = {
        "cycle": st.session_state.cycle,
        "geometry": geometry,
        "dead": dead,
        "live": live,
        "wind": wind,
        "seismic": seismic,
        "beam": beam,
        "column": column,
        "compliance": compliance,
        "ratio": ratio,
        "energy": energy,
        "carbon": carbon,
        "daylight": daylight,
        "ventilation": ventilation,
        "thought": thought,
        "evolution": evolution,
        "floorplan": floorplan,
        "time": str(datetime.now())
    }

    st.session_state.history.append(evolution)
    st.session_state.city_memory.append(result)

    return result

# =========================================================
# AUTONOMOUS LOOP
# =========================================================

if autonomous:
    st.session_state.autonomous_mode = True
else:
    st.session_state.autonomous_mode = False

if run_cycle:
    latest = run_simulation_cycle()

if st.session_state.autonomous_mode:

    auto_placeholder = st.empty()

    for _ in range(2):
        latest = run_simulation_cycle()

        auto_placeholder.success(
            f"Autonomous Cycle {latest['cycle']} completed"
        )

        time.sleep(1)

# =========================================================
# DISPLAY LATEST RESULT
# =========================================================

if len(st.session_state.city_memory) > 0:

    latest = st.session_state.city_memory[-1]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Evolution", latest["evolution"])

    with col2:
        st.metric("Energy Score", latest["energy"])

    with col3:
        st.metric("Carbon", latest["carbon"])

    with col4:
        st.metric("Utilization", latest["ratio"])

    st.markdown("---")

    # =====================================================
    # AI THOUGHTS
    # =====================================================

    st.subheader("🧠 RANDOM AI Thought Stream")

    for thought in st.session_state.thoughts[-10:][::-1]:
        st.write(f"• {thought}")

    st.markdown("---")

    # =====================================================
    # STRUCTURAL SUMMARY
    # =====================================================

    left, right = st.columns(2)

    with left:

        st.subheader("🏗 Structural Analysis")

        st.write(f"Dead Load: {latest['dead']} kN/m²")
        st.write(f"Live Load: {latest['live']} kN/m²")
        st.write(f"Wind Effect: {latest['wind']} kN")
        st.write(f"Seismic Effect: {latest['seismic']} kN")

        st.write(f"Beam Depth: {latest['beam']} mm")
        st.write(f"Column Size: {latest['column']} mm")

        if latest['compliance'] == 'PASS':
            st.success("Eurocode Compliance: PASS")
        else:
            st.error("Eurocode Compliance: FAIL")

        fig = VisualizationEngine.structural_chart(
            latest['dead'],
            latest['live'],
            latest['wind'],
            latest['seismic']
        )

        st.pyplot(fig)

    with right:

        st.subheader("🏙 Building Geometry")

        st.write(latest['geometry'])

        fig2 = VisualizationEngine.massing_plot(
            latest['geometry']['width'],
            latest['geometry']['depth'],
            latest['geometry']['height']
        )

        st.pyplot(fig2)

    st.markdown("---")

    # =====================================================
    # FLOORPLAN DATA
    # =====================================================

    st.subheader("📐 Generated Floorplan Logic")

    floorplan_df = pd.DataFrame(latest['floorplan'])
    st.dataframe(floorplan_df, use_container_width=True)

    # =====================================================
    # ENVIRONMENTAL ANALYSIS
    # =====================================================

    st.subheader("🌿 Sustainability Intelligence")

    env1, env2, env3 = st.columns(3)

    with env1:
        st.metric("Daylight", latest['daylight'])

    with env2:
        st.metric("Ventilation", latest['ventilation'])

    with env3:
        st.metric("Energy", latest['energy'])

    st.markdown("---")

    # =====================================================
    # EVOLUTION GRAPH
    # =====================================================

    st.subheader("📈 Evolution Graph")

    fig3 = VisualizationEngine.evolution_chart(
        st.session_state.history
    )

    st.pyplot(fig3)

    # =====================================================
    # MEMORY EXPORT
    # =====================================================

    st.subheader("💾 City Brain Memory")

    export_data = json.dumps(
        st.session_state.city_memory,
        indent=2
    )

    st.download_button(
        label="Download AI Memory",
        data=export_data,
        file_name="random_ai_memory.json",
        mime="application/json"
    )

# =========================================================
# EMPTY STATE
# =========================================================

else:

    st.info(
        "Run an evolution cycle to awaken the architectural intelligence core."
    )

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "RANDOM AI • Autonomous Eurocode-Inspired Architectural Intelligence"
)
```

