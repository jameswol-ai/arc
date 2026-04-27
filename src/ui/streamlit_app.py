# src/ui/streamlit_app.py

import streamlit as st
from src.core.engine import WorkflowEngine
from src.memory.memory_store import MemoryStore

st.title("🧠 RANDOM v2 — Living Workflow Engine")

memory = MemoryStore()
engine = WorkflowEngine(memory)

workflow = st.selectbox("Choose workflow", ["default"])
user_input = st.text_area("Input")

if st.button("Run Random 🚀"):
    context = {"input": user_input, "data": {}}

    result, trace = engine.run(workflow, context)

    st.subheader("Execution Trace")
    for step in trace:
        st.write(step)

    st.subheader("Final Output")
    st.json(result.data)

    st.subheader("Memory Snapshot")
    st.json(memory.load())
