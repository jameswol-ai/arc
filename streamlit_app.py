import streamlit as st
import random
import json
import os
from uuid import uuid4
import pandas as pd

# =========================================================
# 🧬 RANDOM V6 — GOD CONSOLE
# =========================================================

st.set_page_config(page_title="Random V6 God Console", layout="wide")

st.title("👁️ RANDOM V6 — GOD CONSOLE")
st.caption("Control evolution. Bend reality. Interfere with civilization.")

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
        "events": []
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
        "fitness": 0
    }

# =========================================================
# 🌍 ENVIRONMENT (GOD EDITABLE)
# =========================================================

st.sidebar.header("🌍 World Controls")

wind = st.sidebar.slider("Wind Force", 0.1, 3.0, 1.0)
resources = st.sidebar.slider("Resource Scarcity", 0.1, 3.0, 1.0)
innovation = st.sidebar.slider("Innovation Reward", 0.1, 3.0, 1.0)

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
# 🧬 EVOLUTION STEP
# =========================================================

def evolve(mem):
    pop = mem["population"]

    # Create initial population
    if not pop:
        pop = [create_genome() for _ in range(20)]

    # Evaluate
    for g in pop:
        g["fitness"] = fitness(g)

    # Sort
    pop = sorted(pop, key=lambda x: x["fitness"], reverse=True)

    # Selection
    survivors = pop[:10]

    # Reproduce
    new_pop = survivors.copy()
    while len(new_pop) < 20:
        p1, p2 = random.sample(survivors, 2)
        child = {}
        for k in ["height", "density", "complexity"]:
            child[k] = random.choice([p1[k], p2[k]])
            if random.random() < 0.2:
                child[k] *= random.uniform(0.8, 1.2)

        child["id"] = uuid4().hex
        child["fitness"] = 0
        new_pop.append(child)

    mem["population"] = new_pop
    mem["generation"] += 1

    # Record history
    best = new_pop[0]
    mem["history"].append({
        "generation": mem["generation"],
        "fitness": best["fitness"],
        "height": best["height"]
    })

    return mem

# =========================================================
# 👁️ GOD ACTIONS
# =========================================================

st.sidebar.header("👁️ God Actions")

if st.sidebar.button("⚡ Force Evolution"):
    memory = evolve(memory)
    memory["events"].append(f"Gen {memory['generation']}: God forced evolution.")

if st.sidebar.button("🌋 Catastrophe"):
    for g in memory["population"]:
        g["fitness"] *= random.uniform(0.1, 0.5)
    memory["events"].append(f"Gen {memory['generation']}: Catastrophe struck.")

if st.sidebar.button("🧬 Inject Super Genome"):
    super_g = {
        "id": uuid4().hex,
        "height": 300,
        "density": 0.2,
        "complexity": 15,
        "fitness": 0
    }
    memory["population"].append(super_g)
    memory["events"].append(f"Gen {memory['generation']}: God injected a superior being.")

if st.sidebar.button("☠️ Kill Weakest"):
    memory["population"] = sorted(memory["population"], key=lambda x: x["fitness"])[:-5]
    memory["events"].append(f"Gen {memory['generation']}: Weak purged.")

# =========================================================
# 📊 DASHBOARD
# =========================================================

st.subheader("📊 Evolution Metrics")

if memory["history"]:
    df = pd.DataFrame(memory["history"])
    st.line_chart(df.set_index("generation"))

# =========================================================
# 🧬 POPULATION VIEW
# =========================================================

st.subheader("🧬 Population")

df_pop = pd.DataFrame(memory["population"])
st.dataframe(df_pop)

# =========================================================
# 📖 EVENT LOG (THE WORLD REMEMBERS YOU)
# =========================================================

st.subheader("📖 Civilization Log")

for e in reversed(memory["events"][-10:]):
    st.write(e)

# =========================================================
# 💾 SAVE
# =========================================================

save_memory(memory)
