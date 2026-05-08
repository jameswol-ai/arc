# =========================================================
# 🏙️ RANDOM vNEXT — LEARNING & OPTIMIZING CITY ENGINE
# Memory + Adaptive Planning + Structural Evolution
# =========================================================

import streamlit as st
import random
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# =========================================================
# 🧠 CITY MEMORY (LEARNING LAYER)
# =========================================================
class CityMemory:
    def __init__(self):
        self.failure_heatmap = {}   # (x,y,z) → frequency
        self.stability_history = []

    def record_failures(self, failed_nodes):
        for node in failed_nodes:
            self.failure_heatmap[node] = self.failure_heatmap.get(node, 0) + 1

    def risk_score(self, x, y):
        score = 0
        for (fx, fy, fz), freq in self.failure_heatmap.items():
            dist = abs(x - fx) + abs(y - fy)
            if dist < 5:
                score += freq
        return score

    def stability_trend(self):
        if not self.stability_history:
            return 1.0
        return sum(self.stability_history[-5:]) / min(5, len(self.stability_history))

# =========================================================
# 🧠 ADAPTIVE CITY PLANNER
# =========================================================
class AdaptivePlanner:
    def __init__(self, memory):
        self.memory = memory

    def generate(self):
        buildings = []

        base_count = 5

        for i in range(base_count):
            x, y = random.randint(0, 25), random.randint(0, 25)

            risk = self.memory.risk_score(x, y)

            # 🧠 learning influence: reduce building density in risky zones
            if risk > 3:
                floors = random.randint(2, 5)
                grid = random.choice([6, 8])  # safer smaller structures
            else:
                floors = random.randint(4, 10)
                grid = random.choice([10, 12, 14])

            buildings.append({
                "id": i,
                "floors": floors,
                "grid": grid,
                "offset": (x, y)
            })

        return buildings

# =========================================================
# 🏗️ STRUCTURAL ENGINE
# =========================================================
class StructuralEngine:
    def build(self, buildings):
        nodes = []

        for b in buildings:
            ox, oy = b["offset"]

            for z in range(b["floors"]):
                for x in range(0, b["grid"], 2):
                    for y in range(0, b["grid"], 2):
                        nodes.append((x + ox, y + oy, z))

        return nodes

# =========================================================
# 🌊 LOAD + FAILURE ENGINE
# =========================================================
class PhysicsEngine:
    def compute_loads(self, nodes):
        loads = {n: 0 for n in nodes}

        max_z = max(n[2] for n in nodes)

        for n in nodes:
            if n[2] == max_z:
                loads[n] += 1.0

        for _ in range(3):
            for (x, y, z), l in list(loads.items()):
                if l <= 0:
                    continue

                below = (x, y, z - 1)
                if below in loads:
                    loads[below] += l * 0.7

        return loads

    def collapse(self, loads, threshold=2.0):
        failed = set()

        for node, l in loads.items():
            if l > threshold:
                failed.add(node)

        return failed

# =========================================================
# 🧪 SIMULATION ENGINE
# =========================================================
class SimEngine:
    def evaluate(self, loads, failed):
        stability = max(0, 1 - len(failed) / max(1, len(loads)))

        return {
            "stability": stability,
            "failures": len(failed)
        }

# =========================================================
# 🧠 CITY ENGINE (LEARNING LOOP)
# =========================================================
class CityEngine:
    def __init__(self):
        self.memory = CityMemory()
        self.planner = AdaptivePlanner(self.memory)
        self.structure = StructuralEngine()
        self.physics = PhysicsEngine()
        self.sim = SimEngine()

    def step(self):
        buildings = self.planner.generate()

        nodes = self.structure.build(buildings)
        loads = self.physics.compute_loads(nodes)
        failed = self.physics.collapse(loads)

        self.memory.record_failures(failed)

        sim = self.sim.evaluate(loads, failed)
        self.memory.stability_history.append(sim["stability"])

        return buildings, nodes, loads, failed, sim, self.memory

# =========================================================
# 🌐 STREAMLIT UI
# =========================================================
st.set_page_config(page_title="Learning City Engine", layout="wide")

st.title("🏙️ RANDOM vNEXT — Learning & Optimizing City")
st.caption("A city that remembers its failures and adapts")

engine = CityEngine()

if st.button("🚀 Next Learning Generation"):

    buildings, nodes, loads, failed, sim, memory = engine.step()

    st.subheader("🏗️ City State")
    st.write(buildings)

    c1, c2 = st.columns(2)
    c1.metric("Stability", round(sim["stability"], 3))
    c2.metric("Failures", sim["failures"])

    st.subheader("🧠 Learning Status")
    st.write("Stability Trend:", round(memory.stability_trend(), 3))
    st.write("Known Weak Zones:", len(memory.failure_heatmap))

    # =====================================================
    # 🌆 3D VISUALIZATION
    # =====================================================
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    xs, ys, zs, colors = [], [], [], []

    for node in nodes:
        x, y, z = node

        xs.append(x)
        ys.append(y)
        zs.append(z)

        if node in failed:
            colors.append(5)
        else:
            colors.append(loads[node])

    sc = ax.scatter(xs, ys, zs, c=colors, cmap='viridis', s=10)

    ax.set_title("🏙️ Learning City Structural Field")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Height")

    plt.colorbar(sc, ax=ax, shrink=0.5)

    st.pyplot(fig)

    st.success("City has learned from its structural past 🧠🏙️")
