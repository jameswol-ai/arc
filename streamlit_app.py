import streamlit as st
import random
import time
import numpy as np

# ---------------------------
# PAGE CONFIG (MUST BE FIRST)
# ---------------------------
st.set_page_config(page_title="Random City Brain", layout="wide")

# ---------------------------
# HEADER
# ---------------------------
st.title("🏙️ Random City Brain")
st.caption("A living, evolving AI city simulation (dependency-safe edition)")

# ---------------------------
# SAFE DATA GENERATOR
# ---------------------------
def generate_data(n=50):
    x = np.linspace(0, 10, n)
    y = np.sin(x) + np.random.normal(0, 0.15, n)
    return x, y

# ---------------------------
# INITIAL STATE
# ---------------------------
if "state" not in st.session_state:
    st.session_state.state = {
        "cycle": 0,
        "population": 10,
        "energy": 100,
        "mood": "stable",
        "history": []
    }

if "agents" not in st.session_state:
    st.session_state.agents = {
        "builder": 1.2,
        "energy": 1.0,
        "nature": 0.8,
        "governor": 1.0
    }

# ---------------------------
# EVOLUTION ENGINE
# ---------------------------
def evolve(state, agents):
    state["cycle"] += 1

    growth = int(random.randint(0, 4) * agents["builder"])
    usage = int(random.randint(1, 5) * agents["energy"])
    regen = int(random.randint(0, 3) * agents["nature"])

    state["population"] += growth
    state["energy"] += regen - usage

    # mood system
    if state["energy"] < 20:
        state["mood"] = "critical"
    elif state["population"] > 80:
        state["mood"] = "overflow"
    else:
        state["mood"] = "stable"

    state["history"].append(state["population"])

    return state

# ---------------------------
# REFRESH BUTTON
# ---------------------------
col1, col2 = st.columns(2)

with col1:
    if st.button("▶ Run Evolution Cycle"):
        st.session_state.state = evolve(
            st.session_state.state,
            st.session_state.agents
        )
        st.rerun()

with col2:
    auto = st.checkbox("∞ Autonomous Mode")

# ---------------------------
# AUTO LOOP (SAFE)
# ---------------------------
if auto:
    for _ in range(5):
        st.session_state.state = evolve(
            st.session_state.state,
            st.session_state.agents
        )
        time.sleep(0.15)
    st.rerun()

# ---------------------------
# DASHBOARD
# ---------------------------
state = st.session_state.state

st.subheader("📊 System State")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Cycle", state["cycle"])
c2.metric("Population", state["population"])
c3.metric("Energy", state["energy"])
c4.metric("Mood", state["mood"])

# ---------------------------
# VISUALIZATION (NO MATPLOTLIB NEEDED)
# ---------------------------
st.subheader("📈 Population Flow")

if len(state["history"]) > 2:
    st.line_chart(state["history"])
else:
    st.info("Run cycles to generate evolution data.")

# ---------------------------
# CITY INTELLIGENCE (TEXT SIMULATION)
# ---------------------------
st.subheader("🧠 City Thought Engine")

thoughts = [
    "Patterns are forming in the population flow.",
    "Energy fluctuations detected across cycles.",
    "Stability is being negotiated between systems.",
    "Growth is outpacing regulation mechanisms.",
    "Entropy rising… but still within bounds."
]

st.info(random.choice(thoughts))

# ---------------------------
# SIMPLE GRAPH VIEW (NO NETWORKX)
# ---------------------------
st.subheader("🕸️ City Network (Simplified)")

nodes = list(st.session_state.agents.keys())
edges = [
    ("builder", "population"),
    ("energy", "population"),
    ("nature", "energy"),
    ("governor", "builder")
]

graph_text = "digraph city {\n"

for n in nodes:
    graph_text += f'  {n} [label="{n}\\n{st.session_state.agents[n]:.2f}"];\n'

for a, b in edges:
    graph_text += f"  {a} -> {b};\n"

graph_text += "}"

st.graphviz_chart(graph_text)

# ---------------------------
# AGENT CONTROL
# ---------------------------
st.subheader("🎮 Agent Control Panel")

agent = st.selectbox("Select Agent", list(st.session_state.agents.keys()))

if st.button("Boost Agent"):
    st.session_state.agents[agent] *= 1.2
    st.success(f"{agent} amplified.")

if st.button("Stabilize System"):
    for k in st.session_state.agents:
        st.session_state.agents[k] = 1.0
    st.info("System reset to equilibrium.")
