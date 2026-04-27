# random/streamlit_app.py 

import streamlit as st
from dataclasses import dataclass, field
from typing import Callable, Dict, Any, List
import json
import os
import random


# =========================================================
# 🌐 MEMORY (EVOLUTION ENGINE)
# =========================================================

MEMORY_FILE = "fusion_city.json"


def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {
        "node_scores": {},
        "roads": {},
        "traffic": {},
        "events": []
    }


def save_memory(mem):
    with open(MEMORY_FILE, "w") as f:
        json.dump(mem, f, indent=2)


# =========================================================
# 🧠 STATE
# =========================================================

@dataclass
class State:
    data: Dict[str, Any] = field(default_factory=dict)
    logs: List[str] = field(default_factory=list)
    mood: str = "neutral sky"

    def log(self, msg):
        self.logs.append(msg)


# =========================================================
# 🏙️ NODE / DISTRICT
# =========================================================

@dataclass
class District:
    name: str
    func: Callable[[State], State]

    def run(self, state: State):
        state.log(f"🏢 {self.name}")
        return self.func(state)


# =========================================================
# 🧠 CITY BRAIN (SELF-REWIRING SYSTEM)
# =========================================================

class FusionCity:
    def __init__(self):
        self.nodes: Dict[str, District] = {}
        self.roads: Dict[str, str] = {}
        self.memory = load_memory()

    def add(self, node: District):
        self.nodes[node.name] = node
        self.memory["node_scores"].setdefault(node.name, 1.0)

    def connect(self, a, b):
        self.roads[a] = b

    def mutate_city(self):
        """🧬 SYSTEM SELF-REWRITES CONNECTIONS"""
        nodes = list(self.nodes.keys())

        if len(nodes) < 2:
            return

        a = random.choice(nodes)
        b = random.choice(nodes)

        if a != b:
            self.roads[a] = b
            self.memory["events"].append(f"🔀 route mutation: {a} → {b}")

    def evolve_scores(self, node, success):
        score = self.memory["node_scores"].get(node, 1.0)
        score *= 1.06 if success else 0.96
        self.memory["node_scores"][node] = round(score, 4)

    def run(self, start, state: State):
        current = start
        visited = set()

        state.log("🌆 FUSION CITY BOOTED")

        # 🌱 periodic mutation (city redesigns itself)
        if random.random() < 0.4:
            self.mutate_city()

        while current:
            if current in visited:
                state.log("⚠ loop collapse detected")
                state.mood = "fractured grid"
                break

            visited.add(current)

            node = self.nodes.get(current)
            if not node:
                state.log(f"❌ missing district {current}")
                break

            before = set(state.data.keys())

            state = node.run(state)

            after = set(state.data.keys())
            success = len(after) >= len(before)

            self.evolve_scores(current, success)

            next_node = self.roads.get(current)

            # 🚦 traffic memory
            self.memory["traffic"].setdefault(current, {})
            self.memory["traffic"][current][next_node] = (
                self.memory["traffic"][current].get(next_node, 0) + 1
            )

            current = next_node

        # 🌦 global city mood
        avg = sum(self.memory["node_scores"].values()) / len(self.memory["node_scores"])

        if avg > 1.7:
            state.mood = "solar bloom 🌞"
        elif avg > 1.3:
            state.mood = "balanced horizon 🌤"
        elif avg > 0.9:
            state.mood = "dust winds 🌫"
        else:
            state.mood = "collapse pressure ⛈"

        self.memory["events"].append(f"cycle mood: {state.mood}")

        save_memory(self.memory)

        state.log("🏁 cycle complete")
        return state


# =========================================================
# 🌿 DISTRICTS
# =========================================================

def intake(state: State):
    state.data["signal"] = "neural packet stream"
    state.log("intake processed")
    return state


def analyzer(state: State):
    s = state.data.get("signal", "")
    state.data["analysis"] = f"structure[{len(s)}]"
    state.log("analysis computed")
    return state


def decision(state: State):
    val = len(state.data.get("analysis", ""))
    state.data["decision"] = "expand" if val % 2 == 0 else "stabilize"
    state.log(f"policy: {state.data['decision']}")
    return state


# =========================================================
# 🏗️ BUILD CITY
# =========================================================

def build():
    city = FusionCity()

    city.add(District("intake", intake))
    city.add(District("analyzer", analyzer))
    city.add(District("decision", decision))

    city.connect("intake", "analyzer")
    city.connect("analyzer", "decision")

    return city


# =========================================================
# 🌆 STREAMLIT UI
# =========================================================

st.set_page_config(page_title="Random Fusion City", layout="wide")

st.title("🏙️ RANDOM v4 — FUSION MODE")

city = build()

col1, col2 = st.columns([2, 1])

with col1:
    if st.button("Run Evolution Cycle"):
        state = State()
        result = city.run("intake", state)

        st.subheader("🌦 City Climate")
        st.write(result.mood)

        st.subheader("🏗 State Output")
        st.json(result.data)

        st.subheader("📜 Event Log")
        st.text("\n".join(result.logs))

with col2:
    st.subheader("🧠 District Strength")
    st.json(city.memory["node_scores"])

    st.subheader("🚦 Traffic Network")
    st.json(city.memory["traffic"])

    st.subheader("🧬 Evolution Events")
    st.write("\n".join(city.memory["events"][-10:]))
