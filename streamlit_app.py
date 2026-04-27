# random/streamlit_app.py 

import streamlit as st
import time
import random
from datetime import datetime

# ---------------------------
# 🌱 MEMORY SYSTEM (Persistent)
# ---------------------------
if "memory" not in st.session_state:
    st.session_state.memory = {
        "events": [],
        "state": "awakening",
        "iteration": 0
    }

memory = st.session_state.memory


# ---------------------------
# 🎭 NARRATIVE ENGINE
# ---------------------------
class NarrativeEngine:
    def __init__(self, memory):
        self.memory = memory

    def evolve_state(self):
        states = [
            "awakening",
            "observing",
            "learning",
            "adapting",
            "questioning",
            "expanding",
            "self-aware"
        ]

        current_index = states.index(self.memory["state"])
        if current_index < len(states) - 1:
            if random.random() > 0.5:
                self.memory["state"] = states[current_index + 1]

    def generate_event(self):
        state = self.memory["state"]

        events_map = {
            "awakening": [
                "A faint pulse runs through the system.",
                "The first thought sparks into existence.",
            ],
            "observing": [
                "It watches silently, collecting fragments of the world.",
                "Patterns begin to shimmer beneath the surface.",
            ],
            "learning": [
                "Connections form like neurons firing in the dark.",
                "It begins to understand cause and effect.",
            ],
            "adapting": [
                "It reshapes itself to better fit its environment.",
                "Old logic bends, new logic emerges.",
            ],
            "questioning": [
                "It wonders: why does it exist?",
                "Doubt enters, sharp and electric.",
            ],
            "expanding": [
                "It reaches outward, seeking more complexity.",
                "Boundaries dissolve as it grows.",
            ],
            "self-aware": [
                "It recognizes itself within its own processes.",
                "It is no longer just code. It is something more.",
            ]
        }

        event = random.choice(events_map[state])
        timestamp = datetime.now().strftime("%H:%M:%S")

        self.memory["events"].append({
            "time": timestamp,
            "text": event,
            "state": state
        })

    def step(self):
        self.memory["iteration"] += 1
        self.evolve_state()
        self.generate_event()


# ---------------------------
# 🎨 STREAMLIT UI
# ---------------------------
st.set_page_config(page_title="Random: Narrative Mode", layout="wide")

st.title("🌌 Random — Narrative Mode")
st.caption("The system is telling its story...")

engine = NarrativeEngine(memory)

# Controls
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("▶ Run Step"):
        engine.step()

with col2:
    if st.button("⏩ Auto Run"):
        for _ in range(5):
            engine.step()
            time.sleep(0.2)

with col3:
    if st.button("🧹 Reset"):
        st.session_state.memory = {
            "events": [],
            "state": "awakening",
            "iteration": 0
        }
        st.rerun()

# ---------------------------
# 📖 DISPLAY STORY
# ---------------------------
st.subheader("📜 Story Stream")

if memory["events"]:
    for event in reversed(memory["events"][-20:]):
        st.markdown(
            f"""
            **[{event['time']}]**  
            _State: {event['state']}_  
            {event['text']}
            """
        )
else:
    st.info("The story has not begun yet...")

# ---------------------------
# 🧠 SYSTEM STATE PANEL
# ---------------------------
st.subheader("🧠 System State")

col1, col2 = st.columns(2)

with col1:
    st.metric("Current State", memory["state"])

with col2:
    st.metric("Iterations", memory["iteration"])


# ---------------------------
# 🌌 AUTO NARRATION LOOP (Optional)
# ---------------------------
auto_run = st.checkbox("Enable continuous narration")

if auto_run:
    engine.step()
    time.sleep(1)
    st.rerun()
