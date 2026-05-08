# =========================================================
# 🏗️ RANDOM vNEXT — MULTI-AGENT AUTONOMOUS ENGINE
# Planner + Structure + Spatial + Simulation + Critic
# =========================================================

import streamlit as st
import random
import time
import matplotlib.pyplot as plt

# =========================================================
# 🧠 1. PLANNER AGENT
# =========================================================
class PlannerAgent:
    def propose(self):
        return {
            "building_type": random.choice(["residential", "commercial", "industrial"]),
            "floors": random.randint(1, 10),
            "grid_type": random.choice(["orthogonal", "radial", "hybrid"]),
            "density": round(random.uniform(0.3, 0.9), 2),
        }

# =========================================================
# 🧱 2. STRUCTURAL AGENT
# =========================================================
class StructuralAgent:
    def build(self, floors, grid_type):
        structure = []

        for f in range(floors):
            spacing = 3 + f * 0.15
            cols = []

            for x in range(0, 20, max(2, int(spacing))):
                for y in range(0, 20, max(2, int(spacing))):
                    cols.append((x, y))

            structure.append({
                "floor": f,
                "columns": cols
            })

        return structure

# =========================================================
# 🧭 3. SPATIAL AGENT
# =========================================================
class SpatialAgent:
    def layout(self, building_type, structure):
        floorplans = []

        for floor in structure:
            base = len(floor["columns"])

            if building_type == "residential":
                rooms = base // 3
            elif building_type == "commercial":
                rooms = base // 2
            else:
                rooms = base // 4

            floorplans.append({
                "floor": floor["floor"],
                "rooms": rooms,
                "circulation": max(1, rooms // 4)
            })

        return floorplans

# =========================================================
# 🧪 4. SIMULATION AGENT
# =========================================================
class SimulationAgent:
    def evaluate(self, structure, floors):
        total_cols = sum(len(f["columns"]) for f in structure)

        load = total_cols * floors
        stability = max(0.0, 1.0 - load / 6000)

        efficiency = random.uniform(0.4, 0.95)

        return {
            "stability": round(stability, 3),
            "efficiency": round(efficiency, 3),
            "risk": round(1 - stability, 3)
        }

# =========================================================
# 🧬 5. CRITIC / EVOLUTION AGENT
# =========================================================
class CriticAgent:
    def score(self, sim):
        return round((sim["stability"] * 0.6) + (sim["efficiency"] * 0.4), 3)

    def mutate(self, proposal):
        proposal["floors"] = max(1, proposal["floors"] + random.choice([-1, 0, 1]))
        proposal["density"] = min(1.0, max(0.2, proposal["density"] + random.uniform(-0.1, 0.1)))
        return proposal

# =========================================================
# 🤝 MULTI-AGENT ORCHESTRATOR
# =========================================================
class MultiAgentEngine:
    def __init__(self):
        self.planner = PlannerAgent()
        self.structure = StructuralAgent()
        self.spatial = SpatialAgent()
        self.sim = SimulationAgent()
        self.critic = CriticAgent()

    def run(self, iterations=3):
        proposal = self.planner.propose()
        history = []

        for i in range(iterations):

            # 🧱 structure phase
            structure = self.structure.build(
                proposal["floors"],
                proposal["grid_type"]
            )

            # 🧭 spatial phase
            layout = self.spatial.layout(
                proposal["building_type"],
                structure
            )

            # 🧪 simulation phase
            sim = self.sim.evaluate(structure, proposal["floors"])

            # 🧬 critique phase
            score = self.critic.score(sim)

            history.append({
                "proposal": proposal.copy(),
                "score": score,
                "sim": sim,
                "grid_size": sum(len(f["columns"]) for f in structure)
            })

            if score > 0.8:
                break

            proposal = self.critic.mutate(proposal)

        return history

# =========================================================
# 🖥️ STREAMLIT CONTROL ROOM
# =========================================================
st.set_page_config(page_title="Random Multi-Agent Engine", layout="wide")

st.title("🏗️ RANDOM vNEXT — Multi-Agent Architecture Engine")
st.caption("A studio of competing AI architects building and evolving structures")

engine = MultiAgentEngine()

col1, col2, col3 = st.columns(3)

with col1:
    iterations = st.slider("Agent Iterations", 1, 10, 4)

with col2:
    run = st.button("🚀 Run Multi-Agent Build")

with col3:
    st.metric("Agent System", "ACTIVE 🧠🧱🧭🧪🧬")

# =========================================================
# EXECUTION
# =========================================================
if run:
    st.subheader("🤝 Multi-Agent Design Cycle Starting...")

    history = engine.run(iterations)

    for i, h in enumerate(history):
        st.markdown(f"### Cycle {i+1}")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Score", h["score"])
        c2.metric("Stability", h["sim"]["stability"])
        c3.metric("Efficiency", h["sim"]["efficiency"])
        c4.metric("Risk", h["sim"]["risk"])

        st.write("Proposal:", h["proposal"])

        fig, ax = plt.subplots()
        ax.bar(["Structural Complexity"], [h["grid_size"]])
        st.pyplot(fig)

        time.sleep(0.2)

    st.success("Multi-agent convergence complete 🏗️🧠")
