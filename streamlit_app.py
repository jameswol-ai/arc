# random/streamlit_app.py 

import streamlit as st import random import time from datetime import datetime

-----------------------------

🧠 Session Memory (Persistent per run)

-----------------------------

if "history" not in st.session_state: st.session_state.history = []

if "best" not in st.session_state: st.session_state.best = None

-----------------------------

⚙️ Evolution Functions

-----------------------------

def generate_workflow(): steps = ["concept", "climate", "structure", "energy", "aesthetic"] random.shuffle(steps) return steps

def mutate(workflow): new = workflow.copy() if random.random() < 0.5: i, j = random.sample(range(len(new)), 2) new[i], new[j] = new[j], new[i] if random.random() < 0.3: new.append("experimental") return new

def fitness(workflow): base = len(workflow) creativity = workflow.count("experimental") * 2 randomness = random.uniform(0, 2) return round(base + creativity + randomness, 2)

-----------------------------

🎛️ UI Controls

-----------------------------

st.title("🧬 Random Evolution Dashboard")

mode = st.selectbox("Evolution Mode", ["Conservative", "Exploration", "Chaos"]) run_button = st.button("Run Evolution Cycle")

Mode tuning

if mode == "Conservative": variants_n = 2 elif mode == "Exploration": variants_n = 4 else: variants_n = 8

-----------------------------

🔁 Evolution Cycle

-----------------------------

if run_button: base = st.session_state.best or generate_workflow()

variants = []
for _ in range(variants_n):
    v = mutate(base)
    score = fitness(v)
    variants.append((v, score))

best_variant = max(variants, key=lambda x: x[1])

st.session_state.best = best_variant[0]

record = {
    "time": datetime.now().strftime("%H:%M:%S"),
    "best_score": best_variant[1],
    "workflow": best_variant[0]
}

st.session_state.history.append(record)

-----------------------------

📊 Visualization

-----------------------------

if st.session_state.history: st.subheader("📈 Evolution Timeline")

scores = [h["best_score"] for h in st.session_state.history]
times = [h["time"] for h in st.session_state.history]

st.line_chart(scores)

st.subheader("🏆 Current Best Workflow")
st.write(st.session_state.best)

st.subheader("🧾 Evolution Log")
for h in reversed(st.session_state.history[-10:]):
    st.write(f"[{h['time']}] Score: {h['best_score']} → {h['workflow']}")

else: st.info("Run the evolution cycle to begin...")

-----------------------------

⏱️ Auto Evolution (Optional)

-----------------------------

auto = st.checkbox("Enable Auto Evolution")

if auto: for _ in range(3): time.sleep(1) st.experimental_rerun()
