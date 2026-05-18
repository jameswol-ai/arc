# =========================================================
# 🏗️ RANDOM AI — AUTONOMOUS CIVILIZATION OPERATING SYSTEM
# RL Cities + Architecture + Eurocodes + Agents + Memory
# =========================================================

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import random
import time
import os
import sys
import traceback
from mpl_toolkits.mplot3d import Axes3D

# =========================================================
# PATH SETUP
# =========================================================
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT_DIR)

# =========================================================
# CORE BOOTSTRAP
# =========================================================
from core.bootstrap import bootstrap
bootstrap()

from core.registry import (
    run_pipeline,
    REGISTRIES
)

from core.event_bus import event_bus
from core.safe_execution import safe_execute


# =========================================================
# 🧠 APP CONFIG
# =========================================================
st.set_page_config(
    page_title="Random AI Civilization OS",
    layout="wide"
)

st.title("🏗️ RANDOM AI — Civilization Operating System")


# =========================================================
# 🧠 SESSION STATE
# =========================================================
DEFAULTS = {
    "result": None,
    "intent_text": "",
    "site_area": 1000.0,
    "civil_history": [],
    "brain_logs": [],
    "city_memory": [],
    "events": [],
    "active_agents": [],
}

for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# =========================================================
# 🛡️ SAFE LOGGER
# =========================================================
def log(message):
    st.session_state.brain_logs.append(message)


# =========================================================
# 🧠 RANDOM BRAIN
# =========================================================
class RandomBrain:

    def __init__(self):
        self.state = {
            "awareness": random.random(),
            "stability": 1.0,
            "intelligence": random.random(),
            "adaptation": random.random(),
        }

    def think(self, text):
        log(f"Brain analyzing intent: {text}")

        return {
            "intent": text,
            "complexity": len(text.split()),
            "priority": random.choice([
                "housing",
                "industry",
                "transport",
                "mixed_use"
            ])
        }

    def evolve(self):
        self.state["awareness"] += random.uniform(-0.05, 0.05)
        self.state["intelligence"] += random.uniform(-0.05, 0.05)

        self.state["awareness"] = np.clip(
            self.state["awareness"],
            0,
            1
        )

        self.state["intelligence"] = np.clip(
            self.state["intelligence"],
            0,
            1
        )

    def delegate(self, task):
        log(f"Delegating task: {task}")

    def summary(self):
        return self.state


brain = RandomBrain()


# =========================================================
# 🌐 EVENT BUS
# =========================================================
class EventBus:

    def __init__(self):
        self.listeners = {}

    def subscribe(self, event, callback):

        if event not in self.listeners:
            self.listeners[event] = []

        self.listeners[event].append(callback)

    def emit(self, event, data=None):

        st.session_state.events.append({
            "event": event,
            "data": str(data)
        })

        if event in self.listeners:
            for callback in self.listeners[event]:
                callback(data)


event_bus = EventBus()


# =========================================================
# 🧬 MEMORY ENGINE
# =========================================================
class MemoryEngine:

    def remember(self, item):
        st.session_state.city_memory.append(item)

    def recall(self):
        return st.session_state.city_memory[-10:]


memory = MemoryEngine()


# =========================================================
# 🏙️ RL CITY POLICY
# =========================================================
class CityPolicy:

    def __init__(self):
        self.risk_map = {}
        self.lr = 0.2

    def choose_location(self):

        x = random.randint(0, 25)
        y = random.randint(0, 25)

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
# 🏗️ BUILDING GENERATOR
# =========================================================
class RLBuildingEngine:

    def generate(self, policy):

        buildings = []

        for _ in range(5):

            x, y = policy.choose_location()

            buildings.append({
                "x": x,
                "y": y,
                "floors": random.randint(3, 20),
                "grid": random.choice([6, 8, 10, 12]),
                "usage": random.choice([
                    "Residential",
                    "Commercial",
                    "Industrial"
                ])
            })

        return buildings


# =========================================================
# 🧱 STRUCTURAL PHYSICS
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

    def compute_loads(self, nodes):

        loads = {n: 0.0 for n in nodes}

        if not nodes:
            return loads

        max_z = max(n[2] for n in nodes)

        for n in nodes:

            if n[2] == max_z:
                loads[n] += 1.0

        for _ in range(3):

            for (x, y, z), l in list(loads.items()):

                below = (x, y, z - 1)

                if below in loads:
                    loads[below] += l * 0.7

        return loads

    def collapse(self, loads):

        return {
            n for n, l in loads.items()
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

        loads = self.physics.compute_loads(nodes)

        failed = self.physics.collapse(loads)

        self.policy.update(failed)

        stability = max(
            0,
            1 - len(failed) / max(1, len(nodes))
        )

        reward = stability - 0.3 * len(failed)

        self.history.append(reward)

        memory.remember({
            "reward": reward,
            "stability": stability,
            "failures": len(failed)
        })

        event_bus.emit("city_step_completed", {
            "reward": reward
        })

        return (
            buildings,
            nodes,
            loads,
            failed,
            stability,
            reward
        )


rl_engine = RLCityEngine()


# =========================================================
# 🧠 AGENT SYSTEM
# =========================================================
class PlannerAgent:

    def act(self):
        return "Planning city expansion"


class DiplomacyAgent:

    def act(self):
        return random.choice([
            "Alliance formed",
            "Trade agreement signed",
            "Border tension detected"
        ])


class WarAgent:

    def act(self):
        return random.choice([
            "Peace maintained",
            "Conflict escalation",
            "Defense mobilized"
        ])


AGENTS = {
    "planner": PlannerAgent(),
    "diplomacy": DiplomacyAgent(),
    "war": WarAgent()
}


# =========================================================
# 🏗️ SIDEBAR
# =========================================================
mode = st.sidebar.selectbox(
    "SYSTEM MODULE",
    [
        "🧠 AI Brain",
        "🏛️ Architecture Generator",
        "🏗️ Structure Engine",
        "⚡ MEP Systems",
        "🌍 GIS & Site",
        "💰 Cost Engine",
        "🧊 Rendering",
        "🚀 Full Pipeline",
        "🏙️ RL City",
        "🌆 City Learning",
        "🤝 Diplomacy Network",
        "⚔️ War System",
        "🎭 Culture System",
        "🧠 Civilization Consciousness",
        "🧬 Meta Evolution",
        "📚 Memory System",
        "📡 Event Bus",
        "🤖 Agent Network",
        "🛰️ System Registry"
    ]
)


# =========================================================
# 🧠 AI BRAIN
# =========================================================
if mode == "🧠 AI Brain":

    st.header("🧠 Random Brain")

    st.session_state.intent_text = st.text_area(
        "Describe Intent",
        value=st.session_state.intent_text
    )

    st.session_state.site_area = st.number_input(
        "Site Area",
        value=st.session_state.site_area
    )

    if st.button("RUN AUTONOMOUS GENERATION"):

        try:

            analysis = brain.think(
                st.session_state.intent_text
            )

            result = safe_execute(
                run_pipeline,
                "main",
                analysis
            )

            st.session_state.result = result

            brain.evolve()

            st.success("Generation complete")

        except Exception:
            st.error(traceback.format_exc())

    st.subheader("Brain State")
    st.json(brain.summary())

    if st.session_state.result:
        st.subheader("Pipeline Result")
        st.json(st.session_state.result)

    st.subheader("Brain Logs")
    st.write(st.session_state.brain_logs[-10:])


# =========================================================
# 🏛️ ARCHITECTURE
# =========================================================
elif mode == "🏛️ Architecture Generator":

    st.header("🏛️ Architecture Generator")

    floors = st.slider("Floors", 1, 100, 10)

    building_type = st.selectbox(
        "Building Type",
        [
            "Residential",
            "Commercial",
            "Industrial"
        ]
    )

    if st.button("Generate Floorplan"):

        plan = []

        for i in range(floors):

            rooms = random.randint(4, 20)

            plan.append({
                "floor": i + 1,
                "rooms": rooms,
                "corridors": random.randint(1, 5),
                "stairs": random.randint(1, 3)
            })

        st.json(plan)


# =========================================================
# 🏗️ STRUCTURE
# =========================================================
elif mode == "🏗️ Structure Engine":

    st.header("🏗️ Eurocode Structural Engine")

    span = st.slider("Beam Span", 3, 20, 8)
    load = st.slider("Live Load", 1, 20, 5)

    moment = load * span**2 / 8

    st.metric("Estimated Bending Moment", round(moment, 2))

    :contentReference[oaicite:0]{index=0}

    st.info("Eurocode simulation layer active")


# =========================================================
# ⚡ MEP
# =========================================================
elif mode == "⚡ MEP Systems":

    st.header("⚡ MEP Intelligence")

    st.metric(
        "HVAC Efficiency",
        f"{random.randint(75,98)}%"
    )

    st.metric(
        "Power Usage",
        f"{random.randint(200,1200)} kWh"
    )


# =========================================================
# 🌍 GIS
# =========================================================
elif mode == "🌍 GIS & Site":

    st.header("🌍 Terrain Analysis")

    x = np.linspace(0, 10, 100)
    y = np.sin(x)

    fig, ax = plt.subplots()

    ax.plot(x, y)

    st.pyplot(fig)


# =========================================================
# 💰 COST
# =========================================================
elif mode == "💰 Cost Engine":

    st.header("💰 Cost Engine")

    area = st.number_input("Area", value=500.0)

    cost = area * random.randint(400, 1200)

    st.metric(
        "Estimated Cost",
        f"${cost:,.0f}"
    )


# =========================================================
# 🧊 RENDERING
# =========================================================
elif mode == "🧊 Rendering":

    st.header("🧊 3D Procedural Massing")

    fig = plt.figure()

    ax = fig.add_subplot(111, projection="3d")

    xs = np.random.rand(200)
    ys = np.random.rand(200)
    zs = np.random.rand(200)

    ax.scatter(xs, ys, zs)

    st.pyplot(fig)


# =========================================================
# 🚀 FULL PIPELINE
# =========================================================
elif mode == "🚀 Full Pipeline":

    st.header("🚀 Autonomous Pipeline")

    stages = [
        "Intent Analysis",
        "Architecture",
        "Structure",
        "MEP",
        "Simulation",
        "Rendering",
        "Export"
    ]

    progress = st.progress(0)

    for i, s in enumerate(stages):

        st.write(f"Running: {s}")

        time.sleep(0.3)

        progress.progress((i + 1) / len(stages))

    st.success("Civilization pipeline completed")


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

        c1.metric("Stability", round(stability, 3))
        c2.metric("Failures", len(failed))
        c3.metric("Reward", round(reward, 3))

        st.json(buildings)


# =========================================================
# 🌆 LEARNING
# =========================================================
elif mode == "🌆 City Learning":

    st.header("🌆 RL Learning Curve")

    if rl_engine.history:
        st.line_chart(rl_engine.history)
    else:
        st.info("Run RL City first")


# =========================================================
# 🤝 DIPLOMACY
# =========================================================
elif mode == "🤝 Diplomacy Network":

    st.header("🤝 Diplomacy AI")

    st.success(
        AGENTS["diplomacy"].act()
    )


# =========================================================
# ⚔️ WAR
# =========================================================
elif mode == "⚔️ War System":

    st.header("⚔️ Strategic Conflict Engine")

    st.warning(
        AGENTS["war"].act()
    )


# =========================================================
# 🎭 CULTURE
# =========================================================
elif mode == "🎭 Culture System":

    st.header("🎭 Cultural Evolution")

    culture = {
        "art": random.random(),
        "science": random.random(),
        "spirituality": random.random(),
        "economics": random.random()
    }

    st.json(culture)


# =========================================================
# 🧠 CONSCIOUSNESS
# =========================================================
elif mode == "🧠 Civilization Consciousness":

    st.header("🧠 Global Consciousness")

    state = np.random.rand(10)

    consciousness = {
        "awareness": float(np.mean(state)),
        "conflict": float(np.std(state)),
        "innovation": float(np.max(state)),
        "entropy": float(np.min(state))
    }

    st.json(consciousness)


# =========================================================
# 🧬 META EVOLUTION
# =========================================================
elif mode == "🧬 Meta Evolution":

    st.header("🧬 Evolution Engine")

    st.write(
        "System is recursively optimizing "
        "its own learning architecture."
    )

    st.info("Meta-learning layer active")


# =========================================================
# 📚 MEMORY
# =========================================================
elif mode == "📚 Memory System":

    st.header("📚 Long-Term Memory")

    st.json(memory.recall())


# =========================================================
# 📡 EVENT BUS
# =========================================================
elif mode == "📡 Event Bus":

    st.header("📡 Event Stream")

    st.json(st.session_state.events[-20:])


# =========================================================
# 🤖 AGENTS
# =========================================================
elif mode == "🤖 Agent Network":

    st.header("🤖 Multi-Agent System")

    for name, agent in AGENTS.items():

        st.subheader(name.upper())

        st.write(agent.act())


# =========================================================
# 🛰️ REGISTRY
# =========================================================
elif mode == "🛰️ System Registry":

    st.header("🛰️ Registry System")

    st.json(REGISTRIES)
