import streamlit as st
import random
import json
import os
from uuid import uuid4

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Random Civilization", layout="wide")

st.title("🧬 RANDOM — Living Civilization (Simple Mode)")
st.caption("Pure Python evolution + AI brain + persistence")

SAVE_FILE = "memory.json"

# =========================
# MEMORY
# =========================
def load_memory():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                return json.load(f)
        except:
            pass

    return {
        "generation": 0,
        "population": [],
        "history": [],
        "events": []
    }

def save_memory(mem):
    with open(SAVE_FILE, "w") as f:
        json.dump(mem, f)

memory = load_memory()

# =========================
# GENOME
# =========================
def create_genome():
    return {
        "id": uuid4().hex[:6],
        "height": random.uniform(10, 200),
        "density": random.uniform(0.1, 1.0),
        "complexity": random.uniform(0, 10),
        "fitness": 0
    }

# =========================
# WORLD SETTINGS
# =========================
st.sidebar.header("🌍 World")

env = {
    "wind": st.sidebar.slider("Wind", 0.1, 3.0, 1.0),
    "resources": st.sidebar.slider("Resources", 0.1, 3.0, 1.0),
    "innovation": st.sidebar.slider("Innovation", 0.1, 3.0, 1.0),
}

# =========================
# FITNESS FUNCTION
# =========================
def fitness(g):
    return (
        g["height"] * env["wind"]
        - g["density"] * env["resources"]
        + g["complexity"] * env["innovation"]
    )

# =========================
# EVOLUTION
# =========================
def evolve(mem):
    pop = mem["population"]

    if not pop:
        pop = [create_genome() for _ in range(15)]

    for g in pop:
        g["fitness"] = fitness(g)

    pop.sort(key=lambda x: x["fitness"], reverse=True)

    survivors = pop[:7]
    new_pop = survivors[:]

    while len(new_pop) < 15:
        p1, p2 = random.sample(survivors, 2)

        child = {
            "id": uuid4().hex[:6],
            "height": random.choice([p1["height"], p2["height"]]) * random.uniform(0.9, 1.1),
            "density": random.choice([p1["density"], p2["density"]]) * random.uniform(0.9, 1.1),
            "complexity": random.choice([p1["complexity"], p2["complexity"]]) * random.uniform(0.9, 1.1),
            "fitness": 0
        }

        new_pop.append(child)

    mem["population"] = new_pop
    mem["generation"] += 1

    best = new_pop[0]

    mem["history"].append({
        "gen": mem["generation"],
        "fitness": best["fitness"]
    })

    mem["events"].append(f"Gen {mem['generation']} evolved")

    return mem

# =========================
# AI BRAIN
# =========================
def brain(mem):
    if len(mem["history"]) < 3:
        return mem

    recent = mem["history"][-3:]
    avg = sum(h["fitness"] for h in recent) / 3

    # Decision logic
    if avg > 120:
        # too stable → chaos
        for g in mem["population"]:
            g["fitness"] *= random.uniform(0.5, 0.9)
        mem["events"].append("🧠 Brain: instability injected")

    elif avg < 40:
        # collapse → boost evolution
        mem = evolve(mem)
        mem["events"].append("🧠 Brain: forced evolution recovery")

    else:
        # normal evolution
        if random.random() < 0.7:
            mem = evolve(mem)
            mem["events"].append("🧠 Brain: natural evolution step")

    return mem

# =========================
# CONTROLS
# =========================
st.sidebar.header("⚙️ Control")

if st.sidebar.button("⚡ Evolve"):
    memory = evolve(memory)

if st.sidebar.button("🧠 Brain Step"):
    memory = brain(memory)

if st.sidebar.button("🌋 Catastrophe"):
    for g in memory["population"]:
        g["fitness"] *= random.uniform(0.2, 0.6)
    memory["events"].append("🌋 catastrophe triggered")

if st.sidebar.button("🧬 Inject Life"):
    memory["population"].append(create_genome())
    memory["events"].append("🧬 new entity injected")

# =========================
# VISUALIZATION (TEXT ONLY)
# =========================
st.subheader("🌆 Civilization")

for g in memory["population"]:
    bar = "█" * int(g["height"] / 10)
    st.write(f"{g['id']} | {bar} | fit={round(g['fitness'],2)}")

# =========================
# HISTORY
# =========================
st.subheader("📊 History")

for h in memory["history"][-10:]:
    st.write(f"Gen {h['gen']} → {round(h['fitness'],2)}")

# =========================
# LOG
# =========================
st.subheader("📖 Events")

for e in reversed(memory["events"][-10:]):
    st.write(e)

# =========================
# SAVE
# =========================
save_memory(memory)
