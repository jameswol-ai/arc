import streamlit as st
import random
import math

# =========================================================
# 🧠 RANDOM AI — RULE-CONSCIOUS EUROCODE ARCHITECT
# =========================================================

st.set_page_config(page_title="Random AI Rule-Conscious Engine", layout="wide")

st.title("🏗️ Random AI — Rule-Conscious Architectural Intelligence")
st.caption("Designs are now evaluated, explained, and filtered through Eurocode-inspired reasoning")

# =========================================================
# EUROCODE CORE (SIMPLIFIED LOGIC LAYERS)
# =========================================================

GAMMA_G = 1.35   # permanent load factor
GAMMA_Q = 1.50   # variable load factor

# =========================================================
# PARAMETERS
# =========================================================

st.sidebar.header("🏢 Design Parameters")

floors = st.sidebar.slider("Floors", 1, 25, 6)
width = st.sidebar.slider("Width (m)", 10, 60, 25)
length = st.sidebar.slider("Length (m)", 10, 100, 40)

gk = st.sidebar.slider("Permanent load Gk", 2.0, 15.0, 5.0)
qk = st.sidebar.slider("Variable load Qk", 1.0, 10.0, 3.0)
strength = st.sidebar.slider("Material strength (MPa)", 10, 80, 30)

mutation = st.sidebar.checkbox("🧬 Enable Evolution Mode")

# =========================================================
# ARCHITECTURE GENOME
# =========================================================

def genome():
    return {
        "density": random.uniform(0.2, 0.6),
        "core_strength": random.uniform(0.1, 0.5),
        "void_ratio": random.uniform(0.0, 0.4),
        "symmetry": random.uniform(0.0, 1.0)
    }

# =========================================================
# FLOORPLAN GENERATION
# =========================================================

def build(gen):
    plan = []
    for f in range(floors):
        floor = []
        for i in range(width // 2):
            row = []
            for j in range(length // 2):
                r = random.random()

                # rule-influenced layout behavior
                threshold = gen["density"]

                if gen["symmetry"] > 0.7 and j < (length // 4):
                    cell = "■"
                else:
                    cell = "■" if r < threshold else "□"

                row.append(cell)
            floor.append(row)
        plan.append(floor)
    return plan

# =========================================================
# 🧠 EUROCODE RULE ENGINE (CONSCIOUS LAYER)
# =========================================================

def rule_engine(gen):
    rules = []
    score = 1.0

    # RULE 1 — excessive void ratio weakens structure
    if gen["void_ratio"] > 0.35:
        rules.append("❌ Excessive void ratio → instability risk (EC stability concern)")
        score -= 0.4

    # RULE 2 — very high density increases load demand
    if gen["density"] > 0.55:
        rules.append("⚠ High density → increased load path demand (EC1 load amplification)")
        score -= 0.2

    # RULE 3 — low core strength = poor vertical load transfer
    if gen["core_strength"] < 0.15:
        rules.append("❌ Weak structural core → ULS risk in vertical load transfer")
        score -= 0.5

    # RULE 4 — symmetry improves load distribution
    if gen["symmetry"] > 0.6:
        rules.append("✔ Symmetry improves load distribution efficiency")
        score += 0.2

    return score, rules

# =========================================================
# STRUCTURAL ANALYSIS (EUROCODE-INSPIRED)
# =========================================================

def structural(gen):
    area = width * length

    Ed = (GAMMA_G * gk + GAMMA_Q * qk) * area * floors

    stress = Ed / (area * (1 - gen["void_ratio"] + 0.4))
    stress_mpa = stress / 1000

    safety = strength / max(stress_mpa, 0.0001)

    # LIMIT STATES
    ULS_ok = safety >= 1.5
    SLS_ok = stress_mpa < (strength * 0.6)

    return Ed, stress_mpa, safety, ULS_ok, SLS_ok

# =========================================================
# FITNESS + CONSCIOUS DECISION
# =========================================================

def evaluate(gen):
    rule_score, rule_explanations = rule_engine(gen)
    Ed, stress, safety, ULS, SLS = structural(gen)

    fitness = rule_score * safety

    decision = "APPROVED 🟢"

    if not ULS:
        decision = "REJECTED ❌ (ULS failure)"
    elif not SLS:
        decision = "WARNING 🟠 (SLS deformation limit)"
    elif fitness < 0.8:
        decision = "CONDITIONAL ⚠ (inefficient design)"

    return fitness, rule_explanations, Ed, stress, safety, decision

# =========================================================
# EVOLUTION LOOP
# =========================================================

def mutate(g):
    return {
        "density": min(max(g["density"] + random.uniform(-0.05, 0.05), 0.1), 0.8),
        "core_strength": min(max(g["core_strength"] + random.uniform(-0.05, 0.05), 0.05), 0.6),
        "void_ratio": min(max(g["void_ratio"] + random.uniform(-0.05, 0.05), 0.0), 0.6),
        "symmetry": min(max(g["symmetry"] + random.uniform(-0.1, 0.1), 0.0), 1.0),
    }

# =========================================================
# RUN
# =========================================================

if st.button("🧠 Generate Conscious Design"):

    g = genome()

    fitness, rules, Ed, stress, safety, decision = evaluate(g)

    st.subheader("🏗️ Architectural Decision")

    st.write("### Decision:")
    st.write(decision)

    st.write("### Eurocode Structural Output")
    st.write(f"Design Load Ed: {Ed:.2f} kN")
    st.write(f"Stress (MPa): {stress:.3f}")
    st.write(f"Safety Factor: {safety:.2f}")

    st.write("### Rule Engine Reasoning")
    for r in rules:
        st.write(r)

    st.subheader("🏢 Generated Floorplan")

    plan = build(g)

    for i, floor in enumerate(plan):
        st.markdown(f"### Floor {i+1}")
        for row in floor:
            st.text(" ".join(row))

# =========================================================
# EVOLUTION MODE
# =========================================================

if mutation:

    st.subheader("🧬 Evolution Cycle (Rule-Conscious)")

    population = [genome() for _ in range(8)]
    history = []

    for i in range(5):
        scored = []

        for g in population:
            fitness, _, _, _, _, _ = evaluate(g)
            scored.append((fitness, g))

        scored.sort(reverse=True, key=lambda x: x[0])

        best = scored[0]
        history.append(best)

        survivors = [g for _, g in scored[:4]]
        population = survivors + [mutate(s) for s in survivors]

    for i, (fit, g) in enumerate(history):
        st.write(f"Generation {i+1} → Fitness {fit:.3f}")
