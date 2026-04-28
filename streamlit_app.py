import streamlit as st
import json
import os
import random
import time
import networkx as nx
import matplotlib.pyplot as plt

# ==============================
# 🌱 MEMORY LAYER
# ==============================
class EvolutionMemory:
    def __init__(self, path="memory.json"):
        self.path = path
        self.data = self.load()

    def load(self):
        if os.path.exists(self.path):
            with open(self.path, "r") as f:
                return json.load(f)
        return {"runs": []}

    def save(self):
        with open(self.path, "w") as f:
            json.dump(self.data, f, indent=2)

    def record_run(self, result):
        self.data["runs"].append(result)
        self.save()

# ==============================
# ⚙️ ENGINE LAYER
# ==============================
class WorkflowEngine:
    def __init__(self, workflow):
        self.workflow = workflow
        self.context = {}

    def run(self):
        story = []
        for step in self.workflow:
            name = step["name"]

            # simulate behavior
            output = f"{name}_result_{random.randint(1,100)}"
            self.context[name] = output

            story.append(f"🔹 {name} executed → {output}")

        return {
            "context": self.context,
            "story": story,
            "steps": [s["name"] for s in self.workflow]
        }

# ==============================
# 🧬 EVOLUTION LAYER
# ==============================
def mutate_workflow(memory, workflow):
    runs = memory.data["runs"]

    # mutate if enough history
    if len(runs) > 2:
        if not any(step["name"] == "mutation_node" for step in workflow):
            workflow.append({
                "name": "mutation_node",
                "output_key": "mutation"
            })

    return workflow

# ==============================
# 🎭 NARRATIVE LAYER
# ==============================
def generate_narrative(result):
    narrative = "🧠 Evolution कथा:\n\n"
    for line in result["story"]:
        narrative += line + "\n"

    narrative += "\n🌱 System learned and adapted.\n"
    return narrative

# ==============================
# 🌐 GRAPH VIEW
# ==============================
def render_graph(steps):
    G = nx.DiGraph()

    for i in range(len(steps)-1):
        G.add_edge(steps[i], steps[i+1])

    fig, ax = plt.subplots()
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_size=3000, ax=ax)

    st.pyplot(fig)

# ==============================
# 🌆 CITY BRAIN VIEW
# ==============================
def render_city(steps):
    st.markdown("### 🌆 City Brain")

    cols = st.columns(len(steps))

    for i, step in enumerate(steps):
        with cols[i]:
            st.metric(label=step, value="ACTIVE")

# ==============================
# 🚀 STREAMLIT UI
# ==============================
st.set_page_config(page_title="Random City Brain", layout="wide")

st.title("🌆 Random: Living City Brain")

memory = EvolutionMemory()

# base workflow
workflow = [
    {"name": "concept_stage"},
    {"name": "climate_check"},
    {"name": "eco_design"}
]

# mutate workflow
workflow = mutate_workflow(memory, workflow)

engine = WorkflowEngine(workflow)

# controls
run_button = st.button("▶️ Run Evolution Cycle")
auto_mode = st.checkbox("♾️ Autonomous Mode")

# ==============================
# RUN LOGIC
# ==============================
def run_cycle():
    result = engine.run()
    memory.record_run(result)
    return result

if run_button or auto_mode:

    result = run_cycle()

    # ==========================
    # 🎭 Narrative Output
    # ==========================
    st.markdown("## 🎭 Evolution Narrative")
    st
