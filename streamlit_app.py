# random/streamlit_app.py 

import streamlit as st

from src.core.engine import WorkflowEngine
from src.stages.sample_stages import (
    concept_stage,
    compliance_stage,
    output_stage,
)

# Define workflow
workflow = {
    "basic_design": [
        {"name": "concept", "function": concept_stage},
        {"name": "compliance", "function": compliance_stage},
        {"name": "output", "function": output_stage},
    ]
}

# UI
st.title("🏗️ AI Architecture Bot")

user_input = st.text_input("Enter project idea:")

if st.button("Run Workflow"):
    engine = WorkflowEngine(workflow)
    engine.set_context("input", user_input)

    results = engine.run_workflow("basic_design")

    st.subheader("Results:")
    for r in results:
        st.write(r)
