# random/streamlit_app.py 

import streamlit as st

from src.core.engine import WorkflowEngine
from src.stages.basic_stages import (
    concept_stage,
    compliance_stage,
    output_stage
)

# Register functions
functions = {
    "concept_stage": concept_stage,
    "compliance_stage": compliance_stage,
    "output_stage": output_stage,
}

# Define workflow
workflow = {
    "basic_design": [
        {"name": "concept_stage"},
        {"name": "compliance_stage"},
        {"name": "output_stage"},
    ]
}

# Streamlit UI
st.title("🏗️ AI Architecture Bot")

user_input = st.text_input("Enter your project idea:")

if st.button("Run Workflow"):
    engine = WorkflowEngine(workflow, functions)
    engine.set_context("input", user_input)

    result = engine.run_workflow("basic_design")

    st.subheader("Results:")
    for step in result:
        for k, v in step.items():
            st.write(f"**{k}**: {v}")
