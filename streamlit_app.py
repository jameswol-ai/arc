# =========================================================
# 🏙️ RANDOM vNEXT — EVOLVING CITY + COLLAPSE PHYSICS ENGINE
# Generational Growth + Failure Cascades + Load Dynamics
# =========================================================

import streamlit as st
import random
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# =========================================================
# 🧠 CITY PLANNER (EVOLUTIONARY)
# =========================================================
class CityPlanner:
    def generate(self, previous_city=None):
        buildings = []

        base_count = 4 if not previous_city else len(previous_city)

        for i in range(base_count + random.randint(-1, 2)):
            buildings.append({
                "id": i,
                "type": random.choice(["residential", "commercial", "industrial"]),
                "floors": random.randint(3, 10),
                "grid": random.choice([8, 10, 12]),
                "offset": (
                    random.randint(0, 25),
                    random.randint(0, 25)
                )
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
                        nodes.append((x + ox, y + oy, z, b["id"]))

        return nodes

# =========================================================
# 🌊 LOAD + FAILURE ENGINE
# =========================================================
class PhysicsEngine:
    def compute_loads(self, nodes):
        load = {n: 0.0 for n in nodes}

        # top-down initialization
        for n in nodes:
            if n[2] == max(z for _, _, z, _ in nodes):
                load[n] += 1.0

        # propagate
        for _ in range(3):
            for (x, y, z, bid), l in list(load.items()):

                if l <= 0:
                    continue

                below = (x, y, z - 1, bid)
                if below in load:
                    load[below] += l * 0.7

                # lateral diffusion (city stress coupling)
                for other in load:
                    ox, oy, oz, obid = other
                    if obid != bid and abs(x - ox) + abs(y - oy) < 3:
                        load[other] += l * 0.03

        return load

    # =====================================================
    # 🌊 COLLAPSE PROPAGATION
    # =====================================================
    def collapse(self, load_map, threshold=2.2):
        failed = set()

        # initial failures
        for node, l in load_map.items():
            if l > threshold:
                failed.add(node)

        # cascade propagation
        for _ in range(2):
            new_failures = set()

            for node in failed:
                x, y, z, bid = node

                for other in load_map:
                    ox, oy, oz, obid = other

                    if other not in failed:
                        dist = abs(x - ox) + abs(y - oy) + abs(z - oz)

                        if dist <= 2:
                            load_map[other] += 0.4
                            if load_map[other] > threshold:
                                new_failures.add(other)

            failed |= new_failures

        return failed

# =========================================================
# 🧪 CITY SIMULATION
# =========================================================
class CitySim:
    def evaluate(self, load_map, failed):
        loads = list(load_map.values())

        stability = max(0, 1 - (len(failed) / max(1, len(load_map))))
        congestion = min(1, sum(loads) / len(loads))

        return {
            "stability": round(stability, 3),
            "congestion": round(congestion, 3),
            "failures": len(failed)
        }

# =========================================================
# 🧬 CITY EVOLUTION ENGINE
# =========================================================
class CityEngine:
    def __init__(self):
        self.planner = CityPlanner()
        self.structure = StructuralEngine()
        self.physics = PhysicsEngine()
        self.sim = CitySim()

        self.city_state = None

    def step(self):
        buildings = self.planner.generate(self.city_state)

        nodes = self.structure.build(buildings)
        loads = self.physics.compute_loads(nodes)
        failed = self.physics.collapse(loads)

        sim = self.sim.evaluate(loads, failed)

        self.city_state = buildings

        return buildings, nodes, loads, failed, sim

# =========================================================
# 🌐 STREAMLIT UI
# =========================================================
st.set_page_config(page_title="Random Evolving City", layout="wide")

st.title("🏙️ RANDOM vNEXT — Evolving City + Collapse Physics")
st.caption("Generational urban growth with structural failure cascades")

engine = CityEngine()

if st.button("🚀 Next City Generation"):

    buildings, nodes, loads, failed, sim = engine.step()

    st.subheader("🏗️ City State")
    st.write(buildings)

    c1, c2, c3 = st.columns(3)
    c1.metric("Stability", sim["stability"])
    c2.metric("Congestion", sim["congestion"])
    c3.metric("Failures", sim["failures"])

    # =====================================================
    # 🌆 3D VISUALIZATION
    # =====================================================
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    xs, ys, zs, colors = [], [], [], []

    for node in nodes:
        x, y, z, _ = node

        xs.append(x)
        ys.append(y)
        zs.append(z)

        if node in failed:
            colors.append(5)  # collapse spike
        else:
            colors.append(loads[node])

    sc = ax.scatter(xs, ys, zs, c=colors, cmap='plasma', s=12)

    ax.set_title("🏙️ City Load + Collapse Field")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Height")

    plt.colorbar(sc, ax=ax, shrink=0.5, label="Load / Failure Intensity")

    st.pyplot(fig)

    st.warning(f"⚠️ Structural failures detected: {len(failed)}")
