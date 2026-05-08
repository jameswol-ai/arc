# =========================================================
# 🏗️ RANDOM vNEXT — AUTONOMOUS BUILDING GENERATOR ENGINE
# Brain + Structural Genome + Spatial Logic + Evolution Loop
# =========================================================

import streamlit as st
import random
import time
import matplotlib.pyplot as plt

# =========================================================
# 🧠 1. ARCHITECTURE BRAIN
# =========================================================
class ArchitectureBrain:
    def decide(self, context=None):
        return {
            "building_type": random.choice(["residential", "commercial", "industrial"]),
            "floors": random.randint(1, 10),
            "grid": random.choice(["orthogonal", "radial", "hybrid"]),
            "density": round(random.uniform(0.3, 0.9), 2),
        }

# =========================================================
# 🧱 2. STRUCTURAL GENOME
# =========================================================
class StructuralGenome:
    def generate_grid(self, floors, grid_type):
        structure = []
        for f in range(floors):
            spacing = 3 + (f * 0.2)

            columns = []
            for x in range(0, 20, max(2, int(spacing))):
                for y in range(0, 20, max(2, int(spacing))):
                    columns.append((x, y))

            structure.append({
                "floor": f,
                "columns": columns
            })
        return structure

# =========================================================
# 🧭 3. SPATIAL ENGINE (FLOOR PLAN LOGIC)
# =========================================================
class SpatialEngine:
    def generate_floor_plan(self, building_type, grid):
        plans = []

        for floor in grid:
            if building_type == "residential":
                rooms = len(floor["columns"]) // 3
            elif building_type == "commercial":
                rooms = len(floor["columns"]) // 2
            else:
                rooms = len(floor["columns"]) // 4

            plans.append({
                "floor": floor["floor"],
                "rooms": rooms,
                "circulation": max(1, rooms // 3)
            })

        return plans

# =========================================================
# 🧪 4. SIMULATION ENGINE (STABILITY MODEL)
# =========================================================
class SimulationEngine:
    def evaluate(self, grid, floors):
        column_count = sum(len(f["columns"]) for f in grid)

        load_factor = column_count * floors
        stability = max(0.0, 1.0 - (load_factor / 5000))

        efficiency = random.uniform(0.4, 0.95)

        return {
            "stability": round(stability, 3),
            "efficiency": round(efficiency, 3),
            "risk": round(1 - stability, 3)
        }

# =========================================================
# 🧬 5. EVOLUTION ENGINE
# =========================================================
class EvolutionEngine:
    def score(self, sim):
        return round(
            sim["stability"] * 0.5 +
            sim["efficiency"] * 0.5,
            3
        )

    def mutate(self, context):
        context["floors"] = max(1, context["floors"] + random.choice([-1, 0, 1]))
        context["density"] = min(1.0, max(0.2, context["density"] + random.uniform(-0.1, 0.1)))
        return context

# =========================================================
# 🧠 AUTONOMOUS ENGINE ORCHESTRATOR
# =========================================================
class RandomEngine:
    def __init__(self):
        self.brain = ArchitectureBrain()
        self.structure = StructuralGenome()
        self.spatial = SpatialEngine()
        self.sim = SimulationEngine()
        self.evo = EvolutionEngine()

    def run_cycle(self, iterations=3):
        context = self.brain.decide()

        history = []

        for i in range(iterations):
            grid = self.structure.generate_grid(context["floors"], context["grid"])
            layout = self.spatial.generate_floor_plan(context["building_type"], grid)
            sim = self.sim.evaluate(grid, context["floors"])
            score = self.evo.score(sim)

            result = {
                "context": context.copy(),
                "score": score,
                "sim": sim,
                "grid_size": sum(len(f["columns"]) for f in grid)
            }

            history.append(result)

            if score > 0.75:
                break

            context = self.evo.mutate(context)

        return history

# =========================================================
# 🖥️ STREAMLIT UI — CITY CONTROL ROOM
# =========================================================
st.set_page_config(page_title="Random Autonomous Engine", layout="wide")

st.title("🏗️ RANDOM vNEXT — Autonomous Building Generator")
st.caption("A self-evolving architectural intelligence system")

engine = RandomEngine()

col1, col2, col3 = st.columns(3)

with col1:
    iterations = st.slider("Evolution Iterations", 1, 10, 3)

with col2:
    run = st.button("🚀 Generate Autonomous Building")

with col3:
    st.metric("System Status", "ONLINE 🟢")

# =========================================================
# EXECUTION
# =========================================================
if run:
    st.subheader("🧬 Evolution Cycle Starting...")

    history = engine.run_cycle(iterations)

    for i, h in enumerate(history):
        st.markdown(f"### Cycle {i+1}")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Score", h["score"])
        c2.metric("Stability", h["sim"]["stability"])
        c3.metric("Efficiency", h["sim"]["efficiency"])
        c4.metric("Risk", h["sim"]["risk"])

        st.write("Context:", h["context"])

        # Simple visualization of structural complexity
        fig, ax = plt.subplots()
        ax.bar(["Grid Complexity"], [h["grid_size"]])
        ax.set_ylim(0, max(50, h["grid_size"] + 10))
        st.pyplot(fig)

        time.sleep(0.2)

    st.success("Evolution cycle complete 🧠🏗️")
