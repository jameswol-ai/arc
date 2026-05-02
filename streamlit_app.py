import streamlit as st
import random
import json
import os
from uuid import uuid4
import pandas as pd
import numpy as np

# =============================
# SAFE IMPORTS (3D + fallback)
# =============================
try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except Exception:
    HAS_PLOTLY = False

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# =============================
# CONFIG
# =============================
st.set_page_config(page_title="Random V7 Civilization", layout="wide")

st.title("🧬 RANDOM V7 — Living Civilization")
st.caption("A persistent evolving architectural world with memory, control, and form")

SAVE_FILE = "civilization_memory.json"

# =============================
# MEMORY
# =============================
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

# =============================
# GENOME
# =============================
def create_genome():
    return {
        "id": uuid4().hex,
        "height": random.uniform(10, 200),
        "density": random.uniform(0.1, 1.0),
        "complexity": random.uniform(0, 10),
        "fitness": 0
    }

# =============================
# ENVIRONMENT (GOD CONTROL)
# =============================
st.sidebar.header("🌍 World")

env = {
    "wind": st.sidebar.slider("Wind", 0.1, 3.0, 1.0),
    "resources": st.sidebar.slider("Resources", 0.1, 3.0, 1.0),
    "innovation": st.sidebar.slider("Innovation", 0.1, 3.0, 1.0),
}

# =============================
# FITNESS
# =============================
def fitness(g):
    return (
        g["height"] * env["wind"]
        - g["density"] * env["resources"]
        + g["complexity"] * env["innovation"]
    )

# =============================
# EVOLUTION
# =============================
def evolve(mem):
    pop = mem["population"]

    if not pop:
        pop = [create_genome() for _ in range(20)]

    for g in pop:
        g["fitness"] = fitness(g)

    pop = sorted(pop, key=lambda x: x["fitness"], reverse=True)

    survivors = pop[:10]

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

    best = new_pop[0]

    mem["history"].append({
        "generation": mem["generation"],
        "fitness": best["fitness"],
        "height": best["height"]
    })

    # Narrative
    if best["fitness"] > 150:
        event = f"Gen {mem['generation']}: A dominant structure emerged."
    elif best["fitness"] < 20:
        event = f"Gen {mem['generation']}: Weak generation struggled."
    else:
        event = f"Gen {mem['generation']}: Gradual evolution continued."

    mem["events"].append(event)

    return mem

# =============================
# GOD CONSOLE
# =============================
st.sidebar.header("👁️ God Console")

if st.sidebar.button("⚡ Evolve"):
    memory = evolve(memory)

if st.sidebar.button("🌋 Catastrophe"):
    for g in memory["population"]:
        g["fitness"] *= random.uniform(0.1, 0.5)
    memory["events"].append("Catastrophe reshaped the world.")

if st.sidebar.button("🧬 Inject Super Being"):
    memory["population"].append({
        "id": uuid4().hex,
        "height": 300,
        "density": 0.2,
        "complexity": 15,
        "fitness": 0
    })
    memory["events"].append("A god-tier structure appeared.")

if st.sidebar.button("☠️ Purge Weak"):
    memory["population"] = sorted(memory["population"], key=lambda x: x["fitness"])[5:]
    memory["events"].append("Weak structures were erased.")

# =============================
# METRICS
# =============================
st.subheader("📊 Evolution")

if memory["history"]:
    df = pd.DataFrame(memory["history"])
    st.line_chart(df.set_index("generation"))

# =============================
# 3D VISUALIZATION
# =============================
def create_mesh(g):
    h = g["height"]
    d = g["density"] * 10
    c = g["complexity"]

    x = [-d, d, d, -d, -d]
    y = [-d, -d, d, d, -d]
    z = [0]*5

    xt = [xi + np.sin(i+c)*c for i, xi in enumerate(x)]
    yt = [yi + np.cos(i+c)*c for i, yi in enumerate(y)]
    zt = [h]*5

    return x,y,z,xt,yt,zt

st.subheader("🌆 Civilization Form")

if HAS_PLOTLY:
    fig = go.Figure()

    spacing = 50
    grid = int(len(memory["population"])**0.5)+1

    for i,g in enumerate(memory["population"]):
        gx = (i % grid)*spacing
        gy = (i // grid)*spacing

        x,y,z,xt,yt,zt = create_mesh(g)

        x = [xi+gx for xi in x]
        y = [yi+gy for yi in y]
        xt = [xi+gx for xi in xt]
        yt = [yi+gy for yi in yt]

        for j in range(4):
            fig.add_trace(go.Scatter3d(
                x=[x[j], xt[j]],
                y=[y[j], yt[j]],
                z=[z[j], zt[j]],
                mode='lines'
            ))

        fig.add_trace(go.Scatter3d(x=xt,y=yt,z=zt,mode='lines'))

    fig.update_layout(height=700)
    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("Plotly not installed → fallback view")

    heights = [g["height"] for g in memory["population"]]

    fig, ax = plt.subplots()
    ax.bar(range(len(heights)), heights)
    st.pyplot(fig)

# =============================
# POPULATION
# =============================
st.subheader("🧬 Population")
st.dataframe(pd.DataFrame(memory["population"]))

# =============================
# LOG
# =============================
st.subheader("📖 Civilization Log")

for e in reversed(memory["events"][-10:]):
    st.write(e)

# =============================
# SAVE
# =============================
save_memory(memory)
