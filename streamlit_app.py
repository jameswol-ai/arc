import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))


import streamlit as st
import json

# Core engine
from src.core.engine import WorkflowEngine

# Stages
from core.context import Context import concept_stage
from src.stages.compliance_stage import compliance_stage
from src.stages.output_stage import output_stage
from src.stages.recovery_stage import recovery_stage


# -------------------------------
# 🔧 Setup Page Config
# -------------------------------
st.set_page_config(
    page_title="AI Architecture Bot",
    page_icon="🏗️",
    layout="wide"
)

st.title("🏗️ AI Architecture Workflow Engine")
st.caption("Adaptive AI system for architectural design & compliance")


# -------------------------------
# 🧠 Initialize Workflow Engine
# -------------------------------
@st.cache_resource
def load_engine():
    stages = {
        "concept_stage": concept_stage,
        "compliance_stage": compliance_stage,
        "output_stage": output_stage,
        "recovery_stage": recovery_stage,
    }
    return WorkflowEngine(stages)


engine = load_engine()


# -------------------------------
# 📂 Sidebar Controls
# -------------------------------
st.sidebar.header("⚙️ Workflow Controls")

workflow_type = st.sidebar.selectbox(
    "Select Workflow",
    ["basic_design", "eco_design", "custom"]
)

start_stage = st.sidebar.selectbox(
    "Start Stage",
    ["concept_stage", "compliance_stage", "output_stage"]
)

run_button = st.sidebar.button("🚀 Run Workflow")


# -------------------------------
# 🧾 Input Section
# -------------------------------
st.subheader("📥 Project Input")

user_input = st.text_area(
    "Describe your architectural project",
    placeholder="e.g. Eco-friendly school in tropical climate...",
    height=150
)

col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader(
        "Upload JSON Input (optional)",
        type=["json"]
    )

with col2:
    use_sample = st.checkbox("Use Sample Input")


# -------------------------------
# 📦 Load Input Logic
# -------------------------------
def get_input_data():
    if uploaded_file:
        return json.load(uploaded_file)

    if use_sample:
        return {
            "input": "Eco-friendly school in tropical climate",
            "location": "Tropical",
            "priority": "sustainability"
        }

    return {"input": user_input}


# -------------------------------
# ▶️ Run Workflow
# -------------------------------
if run_button:
    if not user_input and not uploaded_file and not use_sample:
        st.warning("⚠️ Please provide input before running.")
        st.stop()

    input_data = get_input_data()

    # Reset engine context
    engine.context.data.clear()

    # Load input into context
    for key, value in input_data.items():
        engine.set_context(key, value)

    # Run workflow
    with st.spinner("🧠 AI is designing..."):
        result = engine.run(start_stage)

    st.success("✅ Workflow completed!")


    # -------------------------------
    # 📊 Results Display
    # -------------------------------
    st.subheader("📊 Workflow Results")

    tab1, tab2, tab3 = st.tabs([
        "🧾 Final Context",
        "📜 Execution History",
        "🔍 Debug View"
    ])

    # 🧾 Final Context
    with tab1:
        st.json(result["final_context"])

    # 📜 Execution History
    with tab2:
        for stage, output in result["history"]:
            with st.expander(f"🔹 {stage}"):
                st.write(output)

    # 🔍 Debug View
    with tab3:
        st.write("### Raw Data")
        st.write(result)


# -------------------------------
# 📈 Optional: Workflow Visualization
# -------------------------------
st.subheader("🗺️ Workflow Map (Conceptual)")

st.markdown("""# random/streamlit_app.py 
