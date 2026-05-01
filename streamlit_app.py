import streamlit as st
import random
import time

# =========================================================
# 🧬 RANDOM AI v4 — DESIGN CIVILIZATION SIMULATOR
# =========================================================

st.set_page_config(page_title="Architecture Civilization AI", layout="wide")

st.title("🏗️🧬 Random AI v4 — Architecture Civilization")
st.caption("Competing, surviving, and reproducing architectural design ideas")

# =========================================================
# POPULATION INITIALIZATION
# =========================================================

if "population" not in st.session_state:
    st.session_state.population = []

    # seed initial "species" of designs
    for i in range(5):
        st.session_state.population.append({
            "id": f"design_{i}",
            "dna": {
                "stability": random.uniform(0.8, 1.5),
                "efficiency": random.uniform(0.8, 1.5),
                "growth": random.uniform(0.8, 1.5),
                "adaptation": random.uniform(0.8, 1.5),
            },
            "age": 0,
            "fitness": 1.0,
            "alive": True
        })

if "cycle" not in st.session_state:
    st.session_state.cycle = 0

# =========================================================
# FITNESS FUNCTION (SURVIVAL RULES)
# =========================================================

def calculate_fitness(individual):
    dna = individual["dna"]

    # weighted survival pressure
    fitness = (
        dna["stability"] * 0.35 +
        dna["efficiency"] * 0.25 +
        dna["adaptation"] * 0.25 +
        dna["growth"] * 0.15
    )

    # randomness (environment chaos)
    fitness += random.uniform(-0.2, 0.2)

    return max(0, fitness)

# =========================================================
# MUTATION ENGINE
# =========================================================

def mutate(parent_dna):
    child = {}

    for gene, value in parent_dna.items():
        mutation = random.uniform(-0.15, 0.15)
        child[gene] = max(0.3, min(2.0, value + mutation))

    return child

# =========================================================
# REPRODUCTION (CROSSOVER SYSTEM)
# =========================================================

def reproduce(population):
    new_population = []

    # sort by fitness
    sorted_pop = sorted(population, key=lambda x: x["fitness"], reverse=True)

    # top survivors
    survivors = sorted_pop[:3]

    # survival pass
    for s in survivors:
        s["age"] += 1
        new_population.append(s)

    # reproduction phase
    while len(new_population) < 6:
        parent_a = random.choice(survivors)
        parent_b = random.choice(survivors)

        child_dna = {}

        for gene in parent_a["dna"]:
            child_dna[gene] = random.choice([
                parent_a["dna"][gene],
                parent_b["dna"][gene]
            ])

        # mutation step
        if random.random() < 0.4:
            child_dna = mutate(child_dna)

        new_population.append({
            "id": f"child_{random.randint(1000,9999)}",
            "dna": child_dna,
            "age": 0,
            "fitness": 1.0,
            "alive": True
        })

    return new_population

# =========================================================
# SIMULATION STEP
# =========================================================

def simulate():
    st.session_state.cycle += 1

    # evaluate fitness
    for individual in st.session_state.population:
        individual["fitness"] = calculate_fitness(individual)

        # death condition
        if individual["fitness"] < 0.8 and random.random() < 0.5:
            individual["alive"] = False

    # remove dead designs
    st.session_state.population = [
        p for p in st.session_state.population if p["alive"]
    ]

    # reproduction phase
    st.session_state.population = reproduce(st.session_state.population)

# =========================================================
# CONTROLS
# =========================================================

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("▶ Run Evolution Cycle"):
        simulate()
        st.rerun()

with col2:
    auto = st.checkbox("∞ Autonomous Civilization Mode")

with col3:
    if st.button("💥 Environmental Collapse Event"):
        # wipe weakest half
        st.session_state.population = sorted(
            st.session_state.population,
            key=lambda x: x["fitness"]
        )[2:]
        st.warning("Collapse event reduced population")

if auto:
    simulate()
    time.sleep(0.3)
    st.rerun()

# =========================================================
# DISPLAY POPULATION
# =========================================================

st.subheader("🌍 Architecture Population")

for ind in st.session_state.population:
    st.write(f"### {ind['id']}")
    st.json({
        "dna": ind["dna"],
        "fitness": round(ind["fitness"], 2),
        "age": ind["age"]
    })

# =========================================================
# GLOBAL METRICS
# =========================================================

st.subheader("📊 Civilization Metrics")

if st.session_state.population:
    avg_fitness = sum(p["fitness"] for p in st.session_state.population) / len(st.session_state.population)
    avg_age = sum(p["age"] for p in st.session_state.population) / len(st.session_state.population)

    c1, c2, c3 = st.columns(3)
    c1.metric("Cycle", st.session_state.cycle)
    c2.metric("Population", len(st.session_state.population))
    c3.metric("Avg Fitness", round(avg_fitness, 2))

# =========================================================
# EVOLUTION INSIGHT ENGINE
# =========================================================

st.subheader("🧠 Civilization Observation")

insights = [
    "Design traits are converging toward stability dominance.",
    "High-efficiency architectures are outcompeting others.",
    "Mutation events are increasing structural diversity.",
    "Environmental pressure is shaping architectural evolution.",
    "Survival favors balanced DNA profiles over extremes."
]

st.info(random.choice(insights))

# =========================================================
# LINEAGE TRACKING (SIMPLIFIED HISTORY)
# =========================================================

st.subheader("📈 Evolution Trend")

if st.session_state.population:
    st.line_chart([p["fitness"] for p in st.session_state.population])
