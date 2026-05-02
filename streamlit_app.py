import streamlit as st
import random
import json
import os
from uuid import uuid4
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# =========================================================
# 🌍 CONFIG
# =========================================================

st.set_page_config(page_title="Random V6 Civilization", layout="wide")

SAVE_FILE = "civilization_memory.json"

# =========================================================
# 🧠 LOAD / SAVE MEMORY
# =========================================================

def load_memory():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    return {
        "generation": 0,
        "population": [],
        "history": [],
        "events": [],
        "civilization_memory": {
            "dominant_height": [],
            "dominant_density": [],
            "eras": []
        }
    }

def save_memory(mem):
    with open(SAVE_FILE, "w") as f:
        json.dump(mem, f, indent=2)

memory = load_memory()

# =========================================================
# 🧬 GENOME
# =========================================================

def create_genome():
    return {
        "id": uuid4().hex,
        "height": random.uniform(10, 200),
        "density": random.uniform(0.1, 1.0),
        "complexity": random.uniform(0, 10),
        "fitness": 0,
        "parents": []
    }

# =========================================================
# 🌍 ENVIRONMENT (GOD CONTROLLED)
# =========================================================

st.sidebar.header("🌍 World Controls")

wind = st.sidebar.slider("Wind", 0.1, 3.0, 1.0)
resources = st.sidebar.slider("Resources", 0.1, 3.0, 1.0)
innovation = st.sidebar.slider("Innovation", 0.1, 3.0, 1.0)

environment = {
    "wind": wind,
    "resources": resources,
    "innovation": innovation
}

# =========================================================
# ⚔️ FITNESS
# =========================================================

def fitness(g):
    return (
        g["height"] * environment["wind"]
        - g["density"] * environment["resources"]
        + g["complexity"] * environment["innovation"]
    )

# =========================================================
# 🧬 SPECIES
# =========================================================

def species_id(g):
    return f"{round(g['height']/50)}-{round(g['density']/0.2)}"

# =========================================================
# 🏛️ ERA DETECTION
# =========================================================

def detect_era(mem):
    h = mem["civilization_memory"]["dominant_height"]
    if len(h) < 5:
        return "Genesis Era"
    if h[-1] > 150:
        return "Age of Giants"
    if h[-1] < 50:
        return "Dwarf Era"
    return "Adaptive Era"

# =========================================================
# 📖 NARRATIVE
# =========================================================

def narrate(gen, stats):
    if stats["extinction"] > 0.6:
        return f"Gen {gen}: A massive collapse reshaped civilization."
    if stats["max_fit"] > 200:
        return f"Gen {gen}: A dominant structure emerged."
    return f"Gen {gen}: Gradual evolution continued."

# =========================================================
# 🧬 EVOLUTION
# =========================================================

def evolve(mem):
    pop = mem["population"]

    if not pop:
        pop = [create_genome() for _ in range(20)]

    # Evaluate
    for g in pop:
        g["fitness"] = fitness(g)

    pop = sorted(pop, key=lambda x: x["fitness"], reverse=True)

    survivors = pop[:10]

    # Stats
    extinction_rate = 1 - (len(survivors) / len(pop))

    # Reproduce
    new_pop = survivors.copy()
    while len(new_pop) < 20:
        p1, p2 = random.sample(survivors, 2)
        child = {}
        for k in ["height", "density", "complexity"]:
            val = random.choice([p1[k], p2[k]])
            if random.random() < 0.2:
                val *= random.uniform(0.8, 1.2)
            child[k] = val

        child
