import streamlit as st
import random
import time
import matplotlib.pyplot as plt

st.set_page_config(page_title="Random City Brain", layout="wide")

st.title("🏙️ Random City Brain")
st.caption("A living, evolving AI city simulation")

# ---------------------------
# 🌱 INITIAL STATE
# ---------------------------
if "city_state" not in st.session_state:
    st.session_state.city_state = {
        "cycle": 0,
        "energy": 100,
        "population": 10,
        "mood": "stable",
        "history": []
    }

if "agents" not in st.session_state:
    st.session_state.agents = {
        "builder": {"bias": 1.2},
        "energy": {"bias": 1.0},
        "nature": {"bias": 0.8},
        "governor": {"bias": 1.0}
    }

if "meta" not in st.session_state:
    st.session_state.meta = {
        "awareness": 0,
        "last_thought": "Initializing consciousness..."
    }

if "mutation_log" not in st.session_state:
    st.session_state.mutation_log = []

# ---------------------------
# ⚙️ EVOLUTION ENGINE
# ---------------------------
def evolve_city(state, agents):
    state["cycle"] += 1

    growth = int(random.randint(0, 4) * agents["builder"]["bias"])
    energy_use = int(random.randint(1, 5) * growth * agents["energy"]["bias"])
    recovery = int(random.randint(0, 3) * agents["nature"]["bias"])

    state["population"] += growth
    state["energy"] += recovery - energy_use

    # Governor balancing
    if state["energy"] < 20:
        agents["builder"]["bias"] *= 0.9
        agents["energy"]["bias"] *= 1.1

    if state["population"] > 60:
        agents["nature"]["bias"] *= 1.2

    # Mood
    if state["energy"] < 20:
        state["mood"] = "critical"
    elif state["population"] > 80:
        state["mood"] = "overflowing"
    else:
        state["mood"] = "adaptive"

    # Memory
    state["history"].append({
        "cycle": state["cycle"],
        "population": state["population"],
        "energy": state["energy"],
        "mood": state["mood"]
    })

    return state

# ---------------------------
# 👁️ REFLECTION
# ---------------------------
def reflect(state, meta):
    energy = state["energy"]
    population = state["population"]

    meta["awareness"] += int((population + energy) / 50)

    if energy < 20:
        thought = "Energy is low... survival is priority."
    elif population > 80:
        thought = "We are expanding rapidly. Stability is uncertain."
    elif meta["awareness"] > 50:
        thought = "I am beginning to understand my own patterns."
    else:
        thought = "Systems are stable. Growth continues."

    meta["last_thought"] = thought
    return meta

# ---------------------------
# 🧬 MUTATION
# ---------------------------
def mutate_agents(state, agents, log):
    energy = state["energy"]
    population = state["population"]

    for name, agent in agents.items():
        old_bias = agent["bias"]

        if energy < 20:
            change = random.uniform(0.05, 0.2)
        elif population > 80:
            change = random.uniform(-0.2, -0.05)
        else:
            change = random.uniform(-0.05, 0.05)

        agent["bias"] += change
        agent["bias"] = max(0.1, min(2.0, agent["bias"]))

        if abs(old_bias - agent["bias"]) > 0.05:
            log.append(f"{name}: {round(old_bias,2)} → {round(agent['bias'],2)}")

    return agents, log

# ---------------------------
# 🕸️ GRAPH
# ---------------------------
def build_graph(agents):
    G = nx.DiGraph()

    for name, data in agents.items():
        G.add_node(name, weight=round(data["bias"], 2))

    G.add_edge("builder", "population", weight=agents["builder"]["bias"])
    G.add_edge("energy", "population", weight=-agents["energy"]["bias"])
    G.add_edge("nature", "energy", weight=agents["nature"]["bias"])
    G.add_edge("governor", "builder", weight=agents["governor"]["bias"])
    G.add_edge("governor", "energy", weight=agents["governor"]["bias"])

    return G

def draw_graph(G):
    pos = nx.spring_layout(G, seed=42)

    plt.figure()
    nx.draw(G, pos, with_labels=True, node_size=2000, font_size=10)

    nx.draw_networkx_edge_labels(
        G, pos,
        edge_labels={(u, v): round(w, 2) for (u, v, w) in G.edges(data="weight")}
    )

    return plt

# ---------------------------
# 🎮 CONTROLS
# ---------------------------
col1, col2 = st.columns(2)

with col1:
    if st.button("▶ Run Evolution Cycle"):
        st.session_state.city_state = evolve_city(
            st.session_state.city_state,
            st.session_state.agents
        )
        st.session_state.meta = reflect(
            st.session_state.city_state,
            st.session_state.meta
        )
        st.session_state.agents, st.session_state.mutation_log = mutate_agents(
            st.session_state.city_state,
            st.session_state.agents,
            st.session_state.mutation_log
        )

with col2:
    auto = st.checkbox("∞ Autonomous Mode")

# ---------------------------
# ♾️ AUTO LOOP
# ---------------------------
if auto:
    for _ in range(20):
        st.session_state.city_state = evolve_city(
            st.session_state.city_state,
            st.session_state.agents
        )
        st.session_state.meta = reflect(
            st.session_state.city_state,
            st.session_state.meta
        )
        st.session_state.agents, st.session_state.mutation_log = mutate_agents(
            st.session_state.city_state,
            st.session_state.agents,
            st.session_state.mutation_log
        )
        time.sleep(0.2)
        st.rerun()

# ---------------------------
# 📊 DISPLAY
# ---------------------------
state = st.session_state.city_state

st.subheader("📊 City State")
c1, c2, c3, c4 = st.columns(4)

c1.metric("Cycle", state["cycle"])
c2.metric("Population", state["population"])
c3.metric("Energy", state["energy"])
c4.metric("Mood", state["mood"])

# ---------------------------
# 🧠 THOUGHT
# ---------------------------
st.subheader("🧠 City Thought")
st.info(st.session_state.meta["last_thought"])
st.metric("Awareness", st.session_state.meta["awareness"])

# ---------------------------
# 📈 HISTORY
# ---------------------------
if state["history"]:
    st.line_chart([h["population"] for h in state["history"]])

# ---------------------------
# 🧬 MUTATION LOG
# ---------------------------
st.subheader("🧬 Mutation Log")
for entry in st.session_state.mutation_log[-5:]:
    st.write(entry)

# ---------------------------
# 🕸️ GRAPH VIEW
# ---------------------------
st.subheader("🕸️ City Brain Network")
G = build_graph(st.session_state.agents)
fig = draw_graph(G)
st.pyplot(fig)

# ---------------------------
# 🎮 GOD MODE
# ---------------------------
st.subheader("🎮 God Mode")

agent_choice = st.selectbox("Select Agent", list(st.session_state.agents.keys()))

if st.button("Boost Agent"):
    st.session_state.agents[agent_choice]["bias"] *= 1.2
