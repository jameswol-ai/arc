import streamlit as st
import random
import time
import pandas as pd
import json
import os

# =========================================================
# 🧬 RANDOM AI v6 — PERSISTENT CIVILIZATION ENGINE
# =========================================================

st.set_page_config(page_title="Architecture Civilization AI", layout="wide")

st.title("🏗️🧬 Random AI v6 — Persistent Living Civilization")
st.caption("Designs evolve, survive, and now REMEMBER their past worlds")

SAVE_FILE = "civilization_world.json"

# =========================================================
# SIDEBAR — WORLD SETTINGS
# =========================================================

st.sidebar.header("🌍 World Controls")

POP_SIZE = st.sidebar.slider("Population Size", 4, 20, 8)
MUTATION_RATE = st.sidebar.slider("Mutation Rate", 0.0, 1.0, 0.35)
ENV_CHAOS = st.sidebar.slider("Environmental Chaos", 0.0, 1.0, 0.2)
SURVIVAL_PRESSURE = st.sidebar.slider("Survival Pressure", 0.0, 2.0, 1.0)

AUTO_MODE = st.sidebar.checkbox("∞ Autonomous Evolution Mode")

st.sidebar.markdown("---")

# =========================================================
# MEMORY SYSTEM
# =========================================================

def save_world():
    world = {
        "cycle": st.session_state.cycle,
        "population": st.session_state.population,
        "history": st.session_state.history,
        "world_id": st.session_state.world_id
    }

    with open(SAVE_FILE, "w") as f:
        json.dump(world, f)

def load_world():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)

        st.session_state.cycle = data["cycle"]
        st.session_state.population = data["population"]
        st.session_state.history = data["history"]
        st.session_state.world_id = data["world_id"]

# =========================================================
# STATE INIT
# =========================================================

if "population" not in st.session_state:
    st.session_state.population = []
    st.session_state.history = []
    st.session_state.cycle = 0
    st.session_state.world_id = f"world_{random.randint(1000,9999)}"

    for i in range(POP_SIZE):
        st.session_state.population.append({
            "id": f"genesis_{i}",
            "dna": {
                "stability": random.uniform(0.6, 1.6),
                "efficiency": random.uniform(0.6, 1.6),
                "growth": random.uniform(0.6, 1.6),
                "adaptation": random.uniform(0.6, 1.6),
            },
            "age": 0,
            "fitness": 1.0,
            "alive": True,
            "lineage": "genesis"
        })

# =========================================================
# FITNESS FUNCTION
# =========================================================

def calculate_fitness(ind):
    d = ind["dna"]

    base = (
        d["stability"] * 0.35 +
        d["efficiency"] * 0.25 +
        d["adaptation"] * 0.25 +
        d["growth"] * 0.15
    )

    noise = random.uniform(-ENV_CHAOS, ENV_CHAOS)

    return max(0.0, base * SURVIVAL_PRESSURE + noise)

# =========================================================
# MUTATION ENGINE
# =========================================================

def mutate(dna):
    new = {}
    for k, v in dna.items():
        delta = random.uniform(-0.2, 0.2) * MUTATION_RATE
        new[k] = max(0.2, min(2.5, v + delta))
    return new

# =========================================================
# REPRODUCTION ENGINE
# =========================================================

def reproduce(pop):
    pop = sorted(pop, key=lambda x: x["fitness"], reverse=True)

    survivors = pop[: max(2, len(pop)//2)]
    new_pop = []

    for s in survivors:
        s["age"] += 1
        new_pop.append(s)

    while len(new_pop) < POP_SIZE:
        a, b = random.sample(survivors, 2)

        child_dna = {}
        for g in a["dna"]:
            child_dna[g] = random.choice([a["dna"][g], b["dna"][g]])

        if random.random() < MUTATION_RATE:
            child_dna = mutate(child_dna)

        new_pop.append({
            "id": f"evo_{random.randint(1000,9999)}",
            "dna": child_dna,
            "age": 0,
            "fitness": 1.0,
            "alive": True,
            "lineage": f"{a['id']}+{b['id']}"
        })

    return new_pop

# =========================================================
# SIMULATION STEP
# =========================================================

def simulate():
    st.session_state.cycle += 1

    for ind in st.session_state.population:
        ind["fitness"] = calculate_fitness(ind)

        if ind["fitness"] < 0.5 and random.random() < 0.4:
            ind["alive"] = False

    st.session_state.population = [
        p for p in st.session_state.population if p["alive"]
    ]

    st.session_state.population = reproduce(st.session_state.population)

    avg_fit = sum(p["fitness"] for p in st.session_state.population) / len(st.session_state.population)

    st.session_state.history.append({
        "cycle": st.session_state.cycle,
        "avg_fitness": avg_fit,
        "population": len(st.session_state.population)
    })

# =========================================================
# CONTROLS
# =========================================================

c1, c2, c3, c4 = st.columns(4)

with c1:
    if st.button("▶ Run Cycle"):
        simulate()
        st.rerun()

with c2:
    if st.button("💥 Collapse Event"):
        st.session_state.population = sorted(
            st.session_state.population,
            key=lambda x: x["fitness"],
            reverse=True
        )[: max(2, len(st.session_state.population)//2)]

with c3:
    if st.button("💾 Save World"):
        save_world()
        st.success("Civilization saved")

with c4:
    if st.button("📂 Load World"):
        load_world()
        st.success("Civilization restored")
        st.rerun()

# =========================================================
# AUTONOMOUS MODE
# =========================================================

if AUTO_MODE:
    time.sleep(0.3)
    simulate()
    st.rerun()

# =========================================================
# WORLD INFO
# =========================================================

st.subheader("🌍 World Identity")
st.write(f"World ID: **{st.session_state.world_id}**")
st.write(f"Cycle: **{st.session_state.cycle}**")

# =========================================================
# POPULATION VIEW
# =========================================================

st.subheader("🧬 Living Population")

df = [{
    "ID": p["id"],
    "Fitness": round(p["fitness"], 3),
    "Age": p["age"],
    "Lineage": p["lineage"]
} for p in st.session_state.population]

st.dataframe(pd.DataFrame(df), use_container_width=True)

with st.expander("Genome Inspector"):
    for p in st.session_state.population:
        st.write(p["id"])
        st.json(p["dna"])

# =========================================================
# METRICS
# =========================================================

st.subheader("📊 Civilization Metrics")

if st.session_state.population:
    avg_fit = sum(p["fitness"] for p in st.session_state.population) / len(st.session_state.population)

    a, b, c = st.columns(3)
    a.metric("Cycle", st.session_state.cycle)
    b.metric("Population", len(st.session_state.population))
    c.metric("Avg Fitness", round(avg_fit, 3))

# =========================================================
# HISTORY
# =========================================================

st.subheader("📈 Evolution Timeline")

if st.session_state.history:
    hist = pd.DataFrame(st.session_state.history)
    st.line_chart(hist.set_index("cycle")[["avg_fitness", "population"]])

# =========================================================
# INSIGHTS
# =========================================================

st.subheader("🧠 Emergent Insight Layer")

insights = [
    "Lineages are forming persistent architectural families.",
    "Environmental chaos is shaping divergent survival strategies.",
    "Stable designs are slowly dominating the ecosystem.",
    "Mutation pressure increases innovation but destabilizes averages.",
    "Civilization memory allows recurring evolutionary patterns."
]

st.info(random.choice(insights))
