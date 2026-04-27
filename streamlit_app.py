# random/streamlit_app.py 

import streamlit as st
from core.engine import WorkflowEngine

st.title("🧠 Random Engine")

if st.button("Run Random"):
    engine = WorkflowEngine()
    result = engine.run()

    # 🧠 Summary (NEW)
    st.subheader("🧠 Summary")
    st.write(result["summary"]["title"])
    st.info(result["summary"]["insight"])

    # ⚙️ Timeline (cleaner view)
    st.subheader("⚙️ Execution Timeline")
    for step in result["timeline"]:
        if step["status"] == "ok":
            st.success(f"{step['stage']} → completed")
        else:
            st.error(f"{step['stage']} → failed")

    # 📦 Context (raw brain state)
    st.subheader("📦 Final Context")
    st.json(result["final_context"])
