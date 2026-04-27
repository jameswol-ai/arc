# random/streamlit_app.py 

import streamlit as st
import time
import random
from datetime import datetime

# ===============================
# 🌱 BASIC WORKFLOW ENGINE (SAFE)
# ===============================

class WorkflowEngine:
    def __init__(self):
        self.state = {
            "cycle": 0,
            "history": [],
            "last_output": None
        }

    def run(self):
        """Run one evolution cycle"""
        self.state["cycle"] += 1

        # Simulated "intelligence"
        outputs = [
            "Generating adaptive building concept...",
            "Analyzing tropical climate response...",
            "Optimizing energy efficiency...",
            "Evolving structural design...",
            "Simulating city-scale layout...",
            "Rewriting internal logic..."
        ]

        result = random.choice(outputs)

        # Save memory
        self.state["last_output"] = result
        self.state["history"].append({
            "cycle": self.state["cycle"],
            "result": result,
            "time": datetime.now().strftime("%H:%M:%S")
        })

        return result


# ===============================
# 🧬 SESSION STATE INIT
# ===============================

if "engine" not in st.session_state:
    st.session_state.engine = WorkflowEngine()

if "running" not in st.session_state:
    st.session_state.running = False


# ===============================
# 🎨 UI CONFIG
# ===============================

st.set_page_config(
    page_title="random",
    layout="wide"
)

st.title("🧠 random — Alive Architecture System")
st.caption("A self-evolving architectural intelligence")


# ===============================
# 🎛️ CONTROLS
# ===============================

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("▶ Start"):
        st.session_state.running = True

with col2:
    if st.button("⏸ Stop"):
        st.session_state.running = False

with col3:
    if st.button("🔄 Reset"):
        st.session_state.engine = WorkflowEngine()


# ===============================
# ⚙️ MAIN LOOP
# ===============================

output_placeholder = st.empty()
history_placeholder = st.empty()

if st.session_state.running:
    for _ in range(5):  # controlled loop to avoid infinite crash
        result = st.session_state.engine.run()

        output_placeholder.success(f"Cycle {st.session_state.engine.state['cycle']}: {result}")

        time.sleep(1)

    st.rerun()


# ===============================
# 📜 HISTORY PANEL
# ===============================

st.subheader("🧾 Evolution History")

history = st.session_state.engine.state["history"]

if history:
    for item in reversed(history[-10:]):
        st.write(
            f"Cycle {item['cycle']} | {item['time']} → {item['result']}"
        )
else:
    st.info("No evolution yet. Start the system.")


# ===============================
# 🌆 FUTURE HOOKS (EXTENSIONS)
# ===============================

st.subheader("🚀 Expansion Hooks")

st.markdown("""
- 🔹 Plug real WorkflowEngine from `/core/engine.py`
- 🔹 Add AI model decisions (OpenAI / local models)
- 🔹 Connect to your **sai** system
- 🔹 Add city visualization layer
- 🔹 Persist memory to file or database
"")
