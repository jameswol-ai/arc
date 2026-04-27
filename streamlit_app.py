# random/streamlit_app.py 

import streamlit as st
import json
import os
import time
import random
import traceback

# =========================================================
# 💾 WORLD PERSISTENCE
# =========================================================

WORLD_FILE = "random_world_state.json"


def load_world():
    if os.path.exists(WORLD_FILE):
        with open(WORLD_FILE, "r") as f:
            return json.load(f)

    return {
        "tick": 0,
        "cities": {
            "architecture_city": 0,
            "repair_city": 0,
            "innovation_city": 0,
            "general_city": 0
        },
        "events": [],
        "narrative": [],
        "energy": 50  # world vitality
    }


def save_world(world):
    with open(WORLD_FILE, "w") as f:
        json.dump(world, f, indent=2)


# =========================================================
# 🌍 AUTONOMOUS WORLD CORE
# =========================================================

class AutonomousWorld:

    def __init__(self, world):
        self.world = world

    # -------------------------
    # 🫀 WORLD PULSE (AUTONOMY ENGINE)
    # -------------------------
    def pulse(self):
        self.world["tick"] += 1

        # energy drift simulation
        drift = random.randint(-3, 5)
        self.world["energy"] = max(0, min(100, self.world["energy"] + drift))

        # spontaneous city activity
        city = random.choice(list(self.world["cities"].keys()))
        self.world["cities"][city] += 1

        event = {
            "type": "pulse",
            "tick": self.world["tick"],
            "city": city,
            "energy": self.world["energy"]
        }

        self.world["events"].append(event)

        self._narrate(event)
        save_world(self.world)

        return event

    # -------------------------
    # 🌐 USER INPUT INTERACTION
    # -------------------------
    def interact(self, data):

        city = self._route(data)

        self.world["cities"][city] += 2  # stronger impact than pulse

        event = {
            "type": "interaction",
            "tick": self.world["tick"],
            "city": city,
            "data": data
        }

        self.world["events"].append(event)

        self._narrate(event)
        save_world(self.world)

        return event

    def _route(self, data):
        d = str(data).lower()

        if "design" in d:
            return "architecture_city"
        elif "error" in d:
            return "repair_city"
        elif "idea" in d:
            return "innovation_city"
        else:
            return "general_city"

    # -------------------------
    # 📖 NARRATIVE GENERATION
    # -------------------------
    def _narrate(self, event):

        if event["type"] == "pulse":
            text = (
                f"World pulse {event['tick']} stirred {event['city']} "
                f"under energy level {event['energy']}."
            )
        else:
            text = (
                f"External signal reshaped {event['city']} at tick {event['tick']}."
            )

        self.world["narrative"].append(text)

    # -------------------------
    # 🧠 AUTONOMOUS BEHAVIOR MODEL
    # -------------------------
    def auto_decay_or_growth(self):

        if self.world["energy"] < 30:
            self.world["narrative"].append("The world grows unstable, entropy rising.")
            self.world["cities"]["repair_city"] += 1

        elif self.world["energy"] > 80:
            self.world["narrative"].append("The world enters expansion bloom.")
            self.world["cities"]["innovation_city"] += 1

    # -------------------------
    # 🔄 FULL AUTONOMOUS STEP
    # -------------------------
    def step(self, user_input=None):

        # autonomous pulse always happens
        pulse_event = self.pulse()

        # optional user influence
        interaction_event = None
        if user_input:
            interaction_event = self.interact(user_input)

        self.auto_decay_or_growth()

        save_world(self.world)

        return {
            "pulse": pulse_event,
            "interaction": interaction_event
        }


# =========================================================
# 🌍 LOAD WORLD
# =========================================================

if "world" not in st.session_state:
    st.session_state.world = load_world()

world = AutonomousWorld(st.session_state.world)


# =========================================================
# 🌐 UI
# =========================================================

st.set_page_config(page_title="Random Autonomous World", layout="wide")

st.title("🌍 Random — Autonomous World Simulation")
st.caption("The world evolves even when you do nothing.")


# =========================================================
# 🎛 CONTROLS
# =========================================================

user_input = st.text_input("Inject influence into world", "")

col1, col2, col3 = st.columns(3)

step_btn = col1.button("Step World (Pulse + Input)")
auto_btn = col2.button("Auto Run (5 Steps)")
save_btn = col3.button("Save World")


# =========================================================
# ⚙️ EXECUTION
# =========================================================

if step_btn:
    try:
        result = world.step(user_input if user_input else None)
        st.success("World stepped forward")
        st.json(result)
    except Exception:
        st.error("World step failed")
        st.code(traceback.format_exc())


if auto_btn:
    try:
        history = []
        for _ in range(5):
            history.append(world.step())
            time.sleep(0.1)

        st.warning("Autonomous sequence complete")
        st.json(history)

    except Exception:
        st.error("Auto run failed")
        st.code(traceback.format_exc())


if save_btn:
    save_world(world.world)
    st.success("World saved")


# =========================================================
# 🧠 WORLD VIEW
# =========================================================

st.divider()

st.subheader("🌍 World State")
st.json(world.world)


# =========================================================
# 📖 NARRATIVE STREAM
# =========================================================

with st.expander("📜 World Narrative"):
    for line in world.world["narrative"][-40:]:
        st.write(line)


# =========================================================
# 🧪 DEBUG PANEL
# =========================================================

with st.expander("Debug Layer"):
    st.write("Tick:", world.world["tick"])
    st.write("Energy:", world.world["energy"])
    st.write("Total Events:", len(world.world["events"]))
