# src/ui/streamlit_app.py

import streamlit as st
from core.engine import WorkflowEngine

st.title("🧬 Random Dual-Layer Mode")

if st.button("Run Engine"):
    engine = WorkflowEngine()
    result = engine.run()

    # 📖 Narrative Layer (human)
    st.subheader("📖 Narrative Layer")
    for line in result["narrative_layer"]["story"]:
        st.write(line)

    st.info(result["narrative_layer"]["reflection"])

    # ⚙️ Machine Layer (system truth)
    st.subheader("⚙️ Machine Layer")
    st.json(result["machine_layer"]["log"])

    st.subheader("📦 Final Context")
    st.json(result["machine_layer"]["context"])

observer = MetaObserver(city.memory)

st.subheader("👁 Meta Observer Report")

report = observer.analyze()

st.write("🧠 Dominant District:", report["dominant_district"])
st.write("⚠ Weakest District:", report["weak_district"])
st.write("🚦 Most Used Route:", report["dominant_route"])
st.write("🌐 System Tendency:", report["system_tendency"])

st.subheader("📜 Recent System Events")
st.write(report["recent_events"])
