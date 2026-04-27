# random/streamlit_app.py 

import streamlit as st
import time
import traceback

# =========================================================
# 🧠 ENGINE LAYER (PRIMARY OR FALLBACK)
# =========================================================

try:
    from src.core.engine import WorkflowEngine
except Exception:
    WorkflowEngine = None


class AliveCore:
    """
    v2 Living System Core:
    - memory stream
    - heartbeat ticks
    - event log evolution
    """

    def __init__(self):
        self.state = {
            "life": "stable",
            "tick": 0,
            "memory": [],
            "events": [],
            "last_input": None
        }

    def ingest(self, data):
        self.state["last_input"] = data
        event = {
            "type": "input",
            "payload": data,
            "tick": self.state["tick"]
        }
        self.state["events"].append(event)
        self.state["memory"].append(f"ingested: {data}")
        return event

    def tick(self):
        self.state["tick"] += 1

        # simulated evolution logic
        if self.state["tick"] % 5 == 0:
            self.state["life"] = "unstable_flux"
        else:
            self.state["life"] = "stable"

        event = {
            "type": "tick",
            "tick": self.state["tick"],
            "state": self.state["life"]
        }

        self.state["events"].append(event)
        self.state["memory"].append(f"tick {self.state['tick']} → {self.state['life']}")

        return event

    def run(self, input_data):
        self.ingest(input_data)
        return {
            "result": f"processed: {input_data}",
            "state": self.state["life"],
            "tick": self.state["tick"]
        }


# =========================================================
# 🧩 ENGINE SELECTOR
# =========================================================

if WorkflowEngine:
    try:
        engine = WorkflowEngine()
        engine_mode = "primary_engine"
    except Exception:
        engine = AliveCore()
        engine_mode = "alive_fallback_core"
else:
    engine = AliveCore()
    engine_mode = "alive_core_only"


# =========================================================
# 🌐 STREAMLIT CONFIG
# =========================================================

st.set_page_config(page_title="Random Alive v2", layout="wide")

st.title("🌱 Random — Alive System v2")
st.caption(f"Mode: {engine_mode}")


# =========================================================
# 🧠 SESSION STATE INIT
# =========================================================

if "alive" not in st.session_state:
    st.session_state.alive = engine


# =========================================================
# 🎛 UI CONTROL PANEL
# =========================================================

user_input = st.text_input("Inject input into system", "")

col1, col2, col3 = st.columns(3)

run_btn = col1.button("Run")
tick_btn = col2.button("Tick Life")
burst_btn = col3.button("Burst Cycle (x5 ticks)")


# =========================================================
# ⚙️ EXECUTION LOGIC
# =========================================================

engine = st.session_state.alive

if run_btn:
    try:
        result = engine.run(user_input)
        st.success("Run complete")
        st.json(result)
    except Exception:
        st.error("Run failed")
        st.code(traceback.format_exc())


if tick_btn:
    try:
        event = engine.tick()
        st.info(f"Tick: {event}")
    except Exception:
        st.error("Tick failed")
        st.code(traceback.format_exc())


if burst_btn:
    try:
        burst = []
        for _ in range(5):
            burst.append(engine.tick())
            time.sleep(0.1)

        st.warning("Burst cycle complete")
        st.json(burst)

    except Exception:
        st.error("Burst failed")
        st.code(traceback.format_exc())


# =========================================================
# 📊 SYSTEM VIEW
# =========================================================

st.divider()

st.subheader("🧠 System State")

st.json(engine.state)


# =========================================================
# 📜 EVENT TRACE
# =========================================================

with st.expander("Event Stream"):
    for e in engine.state["events"][-20:]:
        st.write(e)


# =========================================================
# 🧪 DEBUG PANEL
# =========================================================

with st.expander("Debug Layer"):
    st.write("Engine Type:", type(engine).__name__)
    st.write("Mode:", engine_mode)
    st.write("Tick Count:", engine.state["tick"])
    st.write("Memory Size:", len(engine.state["memory"]))
