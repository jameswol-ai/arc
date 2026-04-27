import streamlit as st
import sys
import os
import traceback

# 🛠 Ensure correct module path (fixes import issues in Streamlit Cloud)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_PATH = os.path.join(BASE_DIR, "src")

if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

# 🎛 Page config
st.set_page_config(
    page_title="AI Architecture Bot",
    layout="wide"
)

# 🏗 UI Header
st.title("🏗️ AI Architecture Bot")
st.caption("Adaptive Workflow Engine for Smart Building Design")

# 📦 Debug panel toggle
with st.expander("⚙️ Debug Console", expanded=False):
    st.write("Python version:", sys.version)
    st.write("Working directory:", BASE_DIR)
    st.write("Sys path:", sys.path)

# 🧠 Safe import loader
def safe_import():
    try:
        from core.engine import WorkflowEngine
        return WorkflowEngine, None
    except Exception as e:
        return None, traceback.format_exc()

WorkflowEngine, import_error = safe_import()

# 🚨 Show import errors clearly
if import_error:
    st.error("❌ Failed to import WorkflowEngine")
    st.code(import_error)
    st.stop()

# 🧩 Define fallback functions (prevents crash if registry missing)
def concept_stage(ctx):
    return f"Concept based on: {ctx.get('input')}"

def final_output(ctx):
    return f"Final Output:\n{ctx.get('concept')}"

# 🧠 Minimal function registry (safe default)
function_registry = {
    "concept_stage": concept_stage,
    "final_output": final_output,
}

# 🗺 Minimal workflow (safe default)
workflow = {
    "basic_design": [
        {"name": "concept_stage", "output_key": "concept"},
        {"name": "final_output", "output_key": "result"},
    ]
}

# ⚙️ Initialize engine safely
def init_engine():
    try:
        engine = WorkflowEngine(workflow, function_registry)
        return engine, None
    except Exception:
        return None, traceback.format_exc()

engine, engine_error = init_engine()

if engine_error:
    st.error("❌ Engine initialization failed")
    st.code(engine_error)
    st.stop()

# 🎯 User Input
user_input = st.text_area(
    "Describe your architectural project:",
    placeholder="e.g. Eco-friendly school in tropical climate"
)

# ▶️ Run button
if st.button("Generate Design"):
    if not user_input.strip():
        st.warning("Please enter a project description.")
    else:
        try:
            engine.set_context("input", user_input)

            result_context = engine.run_workflow("basic_design")

            st.success("✅ Design Generated Successfully")

            st.subheader("📄 Output")
            st.code(result_context.get("result", "No result generated"))

            # 🧬 Show full context (for debugging)
            with st.expander("🧠 Full Context"):
                st.json(result_context)

        except Exception:
            st.error("❌ Error during workflow execution")
            st.code(traceback.format_exc())
