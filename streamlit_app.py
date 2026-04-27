#random/streamlit_app.py 

import streamlit as st
import sys, os
sys.path.append(os.path.abspath("src"))

from core.engine import WorkflowEngine

# 🔧 Fix import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

# ✅ Clean import (NO circular dependency)
from core.engine import WorkflowEngine

# 🌟 Page config
st.set_page_config(page_title="random", layout="wide")

st.title("🧠 random")
st.caption("Adaptive AI Architecture Engine")

# 🧾 User Input
user_input = st.text_area("Describe your architecture idea:", height=200)

# 🚀 Run button
if st.button("Run random"):
    if not user_input.strip():
        st.warning("Please enter something...")
    else:
        with st.spinner("random is thinking..."):
            try:
                engine = WorkflowEngine()

                result = engine.run_workflow({
                    "input": user_input
                })

                st.success("Workflow complete!")

                st.subheader("📊 Output")
                st.json(result)

            except Exception as e:
                st.error(f"Error: {str(e)}")
