# =========================================================
# 🏗️ RANDOM vNEXT — 3D STRUCTURAL LOAD FLOW ENGINE
# Multi-Agent + 3D Visualization + Load Propagation
# =========================================================

import streamlit as st
import random
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# =========================================================
# 🧠 PLANNER AGENT
# =========================================================
class PlannerAgent:
    def propose(self):
        return {
            "building_type": random.choice(["residential", "commercial", "industrial"]),
            "floors": random.randint(3, 8),
            "grid_size": random.choice([10, 12, 14]),
        }

# =========================================================
# 🧱 STRUCTURAL AGENT (3D GRID)
# =========================================================
class StructuralAgent:
    def build(self, floors, grid_size):
        structure = []

        for z in range(floors):
            for x in range(0, grid_size, 2):
                for y in range(0, grid_size, 2):
                    structure.append((x, y, z))

        return structure

# =========================================================
# ⚡ LOAD FLOW ENGINE
# =========================================================
class LoadFlowEngine:
    def compute_loads(self, structure, floors):
        """
        Load starts at top floor and flows downward.
        Each node distributes load to supporting nodes below.
        """

        loads = {node: 0 for node in structure}

        top_nodes = [n for n in structure if n[2] == floors - 1]

        # initialize load at top
        for node in top_nodes:
            loads[node] = 1.0

        # propagate downward
        for z in reversed(range(floors)):
            layer = [n for n in structure if n[2] == z]

            for node in layer:
                x, y, z = node
                above_load = loads.get((x, y, z + 1), 0)

                # distribute load
                loads[node] += above_load * 0.8

                # slight lateral diffusion
                neighbors = [
                    (x+2, y, z),
                    (x-2, y, z),
                    (x, y+2, z),
                    (x, y-2, z),
                ]

                for n in neighbors:
                    if n in loads:
                        loads[n] += above_load * 0.05

        return loads

# =========================================================
# 🧪 SIMULATION AGENT
# =========================================================
class SimulationAgent:
    def evaluate(self, loads):
        max_load = max(loads.values())
        avg_load = sum(loads.values()) / len(loads)

        stability = max(0, 1 - (max_load / 5))
        efficiency = 1 - (avg_load / 2)

        return {
            "stability": round(stability, 3),
            "efficiency": round(efficiency, 3),
            "max_load": round(max_load, 3)
        }

# =========================================================
# 🧬 CRITIC AGENT
# =========================================================
class CriticAgent:
    def score(self, sim):
        return round(sim["stability"] * 0.7 + sim["efficiency"] * 0.3, 3)

# =========================================================
# 🤝 MULTI-AGENT ENGINE
# =========================================================
class Engine:
    def __init__(self):
        self.planner = PlannerAgent()
        self.structure = StructuralAgent()
        self.loadflow = LoadFlowEngine()
        self.sim = SimulationAgent()
        self.critic = CriticAgent()

    def run(self):
        proposal = self.planner.propose()

        structure = self.structure.build(
            proposal["floors"],
            proposal["grid_size"]
        )

        loads = self.loadflow.compute_loads(structure, proposal["floors"])
        sim = self.sim.evaluate(loads)
        score = self.critic.score(sim)

        return proposal, structure, loads, sim, score

# =========================================================
# 🌐 STREAMLIT UI
# =========================================================
st.set_page_config(page_title="Random 3D Load Flow Engine", layout="wide")

st.title("🏗️ RANDOM vNEXT — 3D Structural Load Flow System")
st.caption("Multi-agent architecture + physics-inspired load propagation")

engine = Engine()

if st.button("🚀 Generate 3D Structure + Load Flow"):

    proposal, structure, loads, sim, score = engine.run()

    st.subheader("🧠 Building Proposal")
    st.write(proposal)

    st.subheader("📊 Simulation Results")

    c1, c2, c3 = st.columns(3)
    c1.metric("Stability", sim["stability"])
    c2.metric("Efficiency", sim["efficiency"])
    c3.metric("Score", score)

    # =====================================================
    # 🧊 3D VISUALIZATION
    # =====================================================
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    xs, ys, zs = [], [], []
    colors = []

    for node in structure:
        x, y, z = node
        load = loads[node]

        xs.append(x)
        ys.append(y)
        zs.append(z)

        # intensity mapping (load → color strength)
        colors.append(load)

    sc = ax.scatter(xs, ys, zs, c=colors, cmap='hot', s=20)

    ax.set_title("3D Structural Grid with Load Flow Intensity")
    ax.set_xlabel("X Grid")
    ax.set_ylabel("Y Grid")
    ax.set_zlabel("Floors")

    plt.colorbar(sc, ax=ax, shrink=0.5, label="Load Intensity")

    st.pyplot(fig)

    st.success("3D structural system generated with load propagation 🌊🏗️")
