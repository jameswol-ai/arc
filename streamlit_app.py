# =========================================================
# 🏗️ RANDOM AI — UNIFIED CIVILIZATION SIMULATOR v2
# RL Cities + Diplomacy + Economy + Consciousness
# =========================================================

import streamlit as st
import numpy as np
import time
import random
import matplotlib.pyplot as plt
import networkx as nx
import sys
import os
from mpl_toolkits.mplot3d import Axes3D

# =========================================================
# PATH SETUP
# =========================================================
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.loader import load_pipelines
load_pipelines()

from core.registry import run_pipeline

# =========================================================
# 🧠 SESSION STATE
# =========================================================
if "result" not in st.session_state:
    st.session_state.result = None

if "intent_text" not in st.session_state:
    st.session_state.intent_text = ""

if "site_area" not in st.session_state:
    st.session_state.site_area = 1000.0

if "civil_history" not in st.session_state:
    st.session_state.civil_history = []

if "city_memory" not in st.session_state:
    st.session_state.city_memory = []

if "traffic_history" not in st.session_state:
    st.session_state.traffic_history = []

if "economy_history" not in st.session_state:
    st.session_state.economy_history = []

if "population_history" not in st.session_state:
    st.session_state.population_history = []

# =========================================================
# 🌍 TERRAIN ENGINE
# =========================================================
class TerrainEngine:

    def generate(self, size=50):

        x = np.linspace(-3, 3, size)
        y = np.linspace(-3, 3, size)

        X, Y = np.meshgrid(x, y)

        Z = np.sin(X**2 + Y**2)

        return X, Y, Z


# =========================================================
# 🛣️ ROAD NETWORK ENGINE
# =========================================================
class RoadNetwork:

    def __init__(self):
        self.graph = nx.grid_2d_graph(10, 10)

    def congestion(self):

        return {
            edge: random.uniform(0, 1)
            for edge in self.graph.edges()
        }

    def shortest_path(self):

        try:
            return nx.shortest_path(
                self.graph,
                (0, 0),
                (9, 9)
            )
        except:
            return []


# =========================================================
# 🏢 ZONING ENGINE
# =========================================================
class ZoningEngine:

    def generate(self, size=25):

        zones = np.random.choice(
            [0, 1, 2, 3],
            (size, size)
        )

        return zones


# =========================================================
# 👥 CITIZEN ENGINE
# =========================================================
class CitizenEngine:

    def generate(self, count=100):

        citizens = []

        jobs = [
            "Engineer",
            "Architect",
            "Trader",
            "Scientist",
            "Worker",
            "Planner"
        ]

        for _ in range(count):

            citizens.append({
                "job": random.choice(jobs),
                "income": random.randint(500, 10000),
                "happiness": round(random.uniform(0.3, 1.0), 2),
                "health": round(random.uniform(0.4, 1.0), 2)
            })

        return citizens


# =========================================================
# ⚡ UTILITY ENGINE
# =========================================================
class UtilityEngine:

    def simulate(self):

        power = random.uniform(0.5, 1.0)
        water = random.uniform(0.5, 1.0)
        internet = random.uniform(0.5, 1.0)

        return {
            "power": power,
            "water": water,
            "internet": internet
        }


# =========================================================
# 💰 ECONOMY ENGINE
# =========================================================
class EconomyEngine:

    def simulate(self, population):

        gdp = population * random.randint(1000, 10000)

        inflation = round(random.uniform(1.0, 15.0), 2)

        unemployment = round(random.uniform(1.0, 20.0), 2)

        return {
            "gdp": gdp,
            "inflation": inflation,
            "unemployment": unemployment
        }


# =========================================================
# 🤝 DIPLOMACY ENGINE
# =========================================================
class DiplomacyEngine:

    def relations(self):

        nations = [
            "North Federation",
            "Solar Union",
            "Oceanic Republic",
            "Iron Collective"
        ]

        return {
            nation: random.choice([
                "Allied",
                "Neutral",
                "Hostile"
            ])
            for nation in nations
        }


# =========================================================
# ⚔️ WAR ENGINE
# =========================================================
class WarEngine:

    def simulate(self):

        tension = round(random.uniform(0, 1), 2)

        return {
            "tension": tension,
            "active_conflict": tension > 0.75
        }


# =========================================================
# 🎭 CULTURE ENGINE
# =========================================================
class CultureEngine:

    def evolve(self):

        return {
            "art_index": round(random.uniform(0, 1), 2),
            "innovation": round(random.uniform(0, 1), 2),
            "social_cohesion": round(random.uniform(0, 1), 2)
        }


# =========================================================
# 🧠 CONSCIOUSNESS ENGINE
# =========================================================
class ConsciousnessEngine:

    def evaluate(self):

        state = np.random.rand(20)

        return {
            "collective_awareness": float(np.mean(state)),
            "conflict_pressure": float(np.std(state)),
            "innovation_drive": float(np.max(state)),
            "entropy": float(np.min(state))
        }


# =========================================================
# 🏙️ RL CITY POLICY
# =========================================================
class CityPolicy:

    def __init__(self):

        self.risk_map = {}
        self.lr = 0.2

    def choose_location(self):

        x, y = random.randint(0, 25), random.randint(0, 25)

        if self.risk_map.get((x, y), 0) > 2:
            return self.choose_location()

        return x, y

    def update(self, failed_nodes):

        for n in failed_nodes:

            x, y, z = n

            self.risk_map[(x, y)] = (
                self.risk_map.get((x, y), 0)
                + self.lr
            )


# =========================================================
# 🏗️ RL BUILDING ENGINE
# =========================================================
class RLBuildingEngine:

    def generate(self, policy):

        buildings = []

        for _ in range(10):

            x, y = policy.choose_location()

            buildings.append({
                "x": x,
                "y": y,
                "floors": random.randint(2, 20),
                "grid": random.choice([6, 8, 10, 12]),
                "zone": random.choice([
                    "Residential",
                    "Commercial",
                    "Industrial",
                    "Mixed Use"
                ])
            })

        return buildings


# =========================================================
# 🧱 RL STRUCTURAL PHYSICS
# =========================================================
class RLPhysics:

    def build_nodes(self, buildings):

        nodes = []

        for b in buildings:

            for z in range(b["floors"]):

                for x in range(0, b["grid"], 2):

                    for y in range(0, b["grid"], 2):

                        nodes.append((
                            x + b["x"],
                            y + b["y"],
                            z
                        ))

        return nodes

    def loads(self, nodes):

        load = {n: 0.0 for n in nodes}

        max_z = max(n[2] for n in nodes)

        for n in nodes:

            if n[2] == max_z:
                load[n] += 1.0

        for _ in range(3):

            for (x, y, z), l in list(load.items()):

                below = (x, y, z - 1)

                if below in load:
                    load[below] += l * 0.7

        return load

    def collapse(self, load):

        return {
            n for n, l in load.items()
            if l > 2.0
        }


# =========================================================
# 🏙️ RL CITY ENGINE
# =========================================================
class RLCityEngine:

    def __init__(self):

        self.policy = CityPolicy()
        self.builder = RLBuildingEngine()
        self.physics = RLPhysics()

        self.history = []

    def step(self):

        buildings = self.builder.generate(self.policy)

        nodes = self.physics.build_nodes(buildings)

        loads = self.physics.loads(nodes)

        failed = self.physics.collapse(loads)

        self.policy.update(failed)

        stability = max(
            0,
            1 - len(failed) / max(1, len(nodes))
        )

        reward = (
            stability
            - 0.3 * len(failed)
        )

        self.history.append(reward)

        return (
            buildings,
            nodes,
            loads,
            failed,
            stability,
            reward
        )


# =========================================================
# 🌍 INITIALIZE SYSTEMS
# =========================================================
terrain_engine = TerrainEngine()
road_engine = RoadNetwork()
zone_engine = ZoningEngine()
citizen_engine = CitizenEngine()
utility_engine = UtilityEngine()
economy_engine = EconomyEngine()
diplomacy_engine = DiplomacyEngine()
war_engine = WarEngine()
culture_engine = CultureEngine()
consciousness_engine = ConsciousnessEngine()
rl_engine = RLCityEngine()

# =========================================================
# 🧠 APP CONFIG
# =========================================================
st.set_page_config(
    page_title="Random AI Civilization Engine",
    layout="wide"
)

st.title("🏗️ RANDOM AI — Unified Civilization Simulator")

# =========================================================
# 🧠 INPUT
# =========================================================
user_input = st.text_input(
    "Civilization Intent",
    "Build an autonomous future city"
)

if st.button("Run Core Pipeline"):

    try:

        st.session_state.result = run_pipeline(
            "main",
            user_input
        )

        st.success("Pipeline executed")

    except Exception as e:

        st.error(str(e))

# =========================================================
# 📚 SIDEBAR
# =========================================================
mode = st.sidebar.selectbox(

    "SYSTEM MODULE",

    [
        "AI Brain",
        "Terrain Engine",
        "Road Intelligence",
        "Zoning System",
        "Citizen Simulation",
        "Utility Grid",
        "Economy",
        "Architecture Generator",
        "Structure Engine",
        "GIS & Site",
        "Rendering",
        "🏙️ RL City",
        "🌆 Learning Curve",
        "🤝 Diplomacy Network",
        "⚔️ War Simulator",
        "🎭 Culture System",
        "🧠 Civilization Consciousness",
        "🧬 Meta-Evolution"
    ]
)

# =========================================================
# 🧠 AI BRAIN
# =========================================================
if mode == "AI Brain":

    st.header("🧠 Civilization Brain")

    st.session_state.intent_text = st.text_area(
        "Describe civilization",
        value=st.session_state.intent_text
    )

    st.session_state.site_area = st.number_input(
        "Territory Size",
        value=st.session_state.site_area
    )

    if st.button("GENERATE CIVILIZATION"):

        try:

            st.session_state.result = run_pipeline(
                st.session_state.intent_text,
                st.session_state.site_area
            )

            st.success("Civilization generated")

        except Exception as e:

            st.error(str(e))

    if st.session_state.result:
        st.json(st.session_state.result)

# =========================================================
# 🌍 TERRAIN
# =========================================================
elif mode == "Terrain Engine":

    st.header("🌍 Terrain Simulation")

    X, Y, Z = terrain_engine.generate()

    fig = plt.figure()

    ax = fig.add_subplot(111, projection='3d')

    ax.plot_surface(X, Y, Z)

    st.pyplot(fig)

# =========================================================
# 🛣️ ROAD SYSTEM
# =========================================================
elif mode == "Road Intelligence":

    st.header("🛣️ Road Network")

    congestion = road_engine.congestion()

    path = road_engine.shortest_path()

    st.write("Optimal Path")
    st.write(path)

    st.metric(
        "Average Congestion",
        round(np.mean(list(congestion.values())), 2)
    )

# =========================================================
# 🏢 ZONING
# =========================================================
elif mode == "Zoning System":

    st.header("🏢 Zoning Engine")

    zones = zone_engine.generate()

    fig, ax = plt.subplots()

    ax.imshow(zones)

    st.pyplot(fig)

# =========================================================
# 👥 CITIZENS
# =========================================================
elif mode == "Citizen Simulation":

    st.header("👥 Population Simulation")

    citizens = citizen_engine.generate(200)

    avg_happiness = np.mean([
        c["happiness"] for c in citizens
    ])

    avg_health = np.mean([
        c["health"] for c in citizens
    ])

    st.metric(
        "Average Happiness",
        round(avg_happiness, 2)
    )

    st.metric(
        "Average Health",
        round(avg_health, 2)
    )

    st.json(citizens[:10])

# =========================================================
# ⚡ UTILITIES
# =========================================================
elif mode == "Utility Grid":

    st.header("⚡ Infrastructure Grid")

    utilities = utility_engine.simulate()

    for k, v in utilities.items():

        st.metric(
            k.capitalize(),
            f"{round(v * 100, 1)}%"
        )

# =========================================================
# 💰 ECONOMY
# =========================================================
elif mode == "Economy":

    st.header("💰 Economic Simulation")

    economy = economy_engine.simulate(
        population=random.randint(1000, 100000)
    )

    st.json(economy)

# =========================================================
# 🏛️ ARCHITECTURE
# =========================================================
elif mode == "Architecture Generator":

    st.header("🏛️ Procedural Architecture")

    floors = st.slider("Floors", 1, 80, 10)

    building_type = st.selectbox(
        "Building Type",
        [
            "Residential",
            "Commercial",
            "Industrial"
        ]
    )

    st.write({
        "floors": floors,
        "type": building_type,
        "generated": True
    })

# =========================================================
# 🧱 STRUCTURE
# =========================================================
elif mode == "Structure Engine":

    st.header("🏗️ Structural Analysis")

    st.info(
        "Future Eurocode engine integration active"
    )

# =========================================================
# 🌍 GIS
# =========================================================
elif mode == "GIS & Site":

    st.header("🌍 GIS + Environmental Layer")

    x = np.linspace(0, 20, 200)

    y = np.sin(x) * np.cos(x / 2)

    fig, ax = plt.subplots()

    ax.plot(x, y)

    st.pyplot(fig)

# =========================================================
# 🎨 RENDERING
# =========================================================
elif mode == "Rendering":

    st.header("🧊 3D City Rendering")

    fig = plt.figure()

    ax = fig.add_subplot(111, projection='3d')

    x = np.random.rand(200)
    y = np.random.rand(200)
    z = np.random.rand(200)

    ax.scatter(x, y, z)

    st.pyplot(fig)

# =========================================================
# 🏙️ RL CITY
# =========================================================
elif mode == "🏙️ RL City":

    st.header("🏙️ RL City Simulator")

    if st.button("Run Simulation Step"):

        (
            buildings,
            nodes,
            loads,
            failed,
            stability,
            reward
        ) = rl_engine.step()

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "City Stability",
            round(stability, 3)
        )

        c2.metric(
            "Structural Failures",
            len(failed)
        )

        c3.metric(
            "RL Reward",
            round(reward, 3)
        )

        st.json(buildings)

# =========================================================
# 🌆 LEARNING
# =========================================================
elif mode == "🌆 Learning Curve":

    st.header("📈 Reinforcement Learning History")

    if rl_engine.history:

        st.line_chart(
            rl_engine.history
        )

    else:

        st.info("Run RL City first")

# =========================================================
# 🤝 DIPLOMACY
# =========================================================
elif mode == "🤝 Diplomacy Network":

    st.header("🤝 Global Diplomacy")

    relations = diplomacy_engine.relations()

    st.json(relations)

# =========================================================
# ⚔️ WAR
# =========================================================
elif mode == "⚔️ War Simulator":

    st.header("⚔️ Conflict Engine")

    war = war_engine.simulate()

    st.json(war)

# =========================================================
# 🎭 CULTURE
# =========================================================
elif mode == "🎭 Culture System":

    st.header("🎭 Cultural Evolution")

    culture = culture_engine.evolve()

    st.json(culture)

# =========================================================
# 🧠 CONSCIOUSNESS
# =========================================================
elif mode == "🧠 Civilization Consciousness":

    st.header("🧠 Collective Civilization Mind")

    consciousness = consciousness_engine.evaluate()

    st.json(consciousness)

# =========================================================
# 🧬 META EVOLUTION
# =========================================================
elif mode == "🧬 Meta-Evolution":

    st.header("🧬 Evolution of Civilization")

    st.write("""
    Civilization is recursively redesigning:
    - infrastructure
    - intelligence
    - social systems
    - economy
    - governance
    - adaptation policies
    """)

    st.success(
        "Meta-learning layer operational"
    )
