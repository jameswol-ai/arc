import streamlit as st
import numpy as np
import time
import random
import matplotlib.pyplot as plt
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# IMPORTANT: keep imports at top
@from core.safe_import import get_pipeline
run_pipeline = get_pipeline()

st.session_state.result = run_pipeline(
    st.session_state.intent_text,
    st.session_state.site_area
)
#from export.bim_exporter import export_bim
#from structure.eurocode_engine import structural_assessment
from core.registry import registry

if st.sidebar.checkbox("Show Registered Modules"):
    st.json(registry.list_modules())


# =========================================================
# 🧠 APP CONFIG
# =========================================================
st.set_page_config(page_title="Random AI Control Center", layout="wide")

st.title("🏗️ RANDOM AI — CONTROL CENTER")
st.caption("Generative Architecture + Structure + BIM + Parametric System")


# =========================================================
# SESSION STATE SAFETY
# =========================================================
if "result" not in st.session_state:
    st.session_state.result = None

if "intent_text" not in st.session_state:
    st.session_state.intent_text = ""

if "site_area" not in st.session_state:
    st.session_state.site_area = 1000.0


# =========================================================
# SIDEBAR
# =========================================================
mode = st.sidebar.selectbox(
    "SYSTEM MODULE",
    [
        "AI Brain",
        "Architecture Generator",
        "Structure Engine",
        "MEP Systems",
        "GIS & Site",
        "Cost Engine",
        "Rendering",
        "Export Center",
        "Parametric BIM",
        "Full Pipeline Simulation"
    ]
)


# =========================================================
# 🧠 AI BRAIN
# =========================================================
if mode == "AI Brain":

    st.header("🧠 Design Brain")

    st.session_state.intent_text = st.text_area(
        "Describe building intent",
        value=st.session_state.intent_text
    )

    st.session_state.site_area = st.number_input(
        "Site Area (m²)",
        value=st.session_state.site_area
    )

    # SAFE PIPELINE EXECUTION
    if st.button("RUN FULL GENERATION"):
        try:
            st.session_state.result = run_pipeline(
                st.session_state.intent_text,
                st.session_state.site_area
            )
            st.success("Pipeline executed successfully")

        except Exception as e:
            st.error(f"Pipeline failed: {str(e)}")


    # OUTPUT DISPLAY
    if st.session_state.result:

        result = st.session_state.result

        st.subheader("ARCHITECTURE")
        st.json(result["current_design"]["architecture"])

        st.subheader("STRUCTURE")
        st.json(result["current_design"]["structure"])

        st.subheader("SCORE")
        st.json(result["current_design"]["score"])

        st.subheader("NEXT EVOLUTION SEED")
        st.json(result["next_generation_seed"])


# =========================================================
# 🏛️ ARCHITECTURE
# =========================================================
elif mode == "Architecture Generator":

    st.header("🏛️ Architecture Engine")

    floors = st.slider("Number of Floors", 1, 50, 5)

    if st.button("Generate Floorplan"):
        for i in range(floors):
            st.write(f"Floor {i+1}: grid generated")

        st.info("Zoning + circulation simulated")


# =========================================================
# 🏗️ STRUCTURE ENGINE
# =========================================================
elif mode == "Structure Engine":

    st.header("🏗️ Eurocode Structural Analysis")

    span = st.slider("Beam Span (m)", 2.0, 12.0, 6.0)
    area = st.number_input("Floor Area (m²)", value=500.0)
    height = st.slider("Column Height (m)", 2.5, 6.0, 3.2)

    if st.button("Run Structural Check"):

        load = area * 0.6

        result = structural_assessment(span, load, load * 0.6, height)

        st.json(result)


# =========================================================
# ⚡ MEP
# =========================================================
elif mode == "MEP Systems":

    st.header("MEP Systems")

    st.metric("HVAC", f"{random.randint(70, 98)}%")
    st.metric("Water Flow", f"{random.randint(60, 100)} L/s")
    st.metric("Power Load", f"{random.randint(50, 120)} kW")


# =========================================================
# 🌍 GIS
# =========================================================
elif mode == "GIS & Site":

    st.header("Terrain Analysis")

    slope = random.uniform(0, 35)
    st.write(f"Slope: {slope:.2f}°")

    fig, ax = plt.subplots()
    x = np.linspace(0, 10, 100)
    y = np.sin(x) + slope / 10
    ax.plot(x, y)

    st.pyplot(fig)


# =========================================================
# 💰 COST
# =========================================================
elif mode == "Cost Engine":

    st.header("Cost Estimation")

    area = st.number_input("Area", value=500.0)

    cost = area * random.randint(400, 1200)

    st.metric("Total Cost", f"${cost:,.0f}")


# =========================================================
# 🧊 RENDERING
# =========================================================
elif mode == "Rendering":

    st.header("3D Massing")

    size = st.slider("Size", 1, 10, 5)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")

    ax.scatter(
        np.random.rand(50) * size,
        np.random.rand(50) * size,
        np.random.rand(50) * size
    )

    st.pyplot(fig)


# =========================================================
# 📦 EXPORT
# =========================================================
elif mode == "Export Center":

    st.header("BIM Export")

    if st.session_state.result:

        bim = st.session_state.result["bim"]

        st.metric("Elements", len(bim.elements))

        sample_id = list(bim.elements.keys())[0]
        st.json(bim.elements[sample_id].__dict__)

        st.download_button(
            "Download BIM JSON",
            data=export_bim(bim),
            file_name="bim_model.json"
        )

    else:
        st.warning("Run AI Brain first")


# =========================================================
# 🧬 PARAMETRIC BIM
# =========================================================
elif mode == "Parametric BIM":

    st.header("Parametric BIM")

    if st.session_state.result:

        engine = st.session_state.result["parametric_engine"]

        fh = st.slider("Floor Height", 2.5, 5.0, 3.2)
        gs = st.slider("Grid Spacing", 3.0, 8.0, 4.0)
        wt = st.slider("Wall Thickness", 0.1, 0.5, 0.2)

        if st.button("Update BIM"):
            engine.set_parameter("floor_height", fh)
            engine.set_parameter("grid_spacing", gs)
            engine.set_parameter("wall_thickness", wt)

            st.success("Updated")

    else:
        st.warning("Run AI Brain first")


# =========================================================
# 🚀 FULL PIPELINE
# =========================================================
elif mode == "Full Pipeline Simulation":

    st.header("System Simulation")

    if st.button("Run Simulation"):

        steps = [
            "AI",
            "Architecture",
            "Structure",
            "MEP",
            "Cost",
            "Rendering",
            "Export"
        ]

        p = st.progress(0)

        for i, s in enumerate(steps):
            st.write(s)
            time.sleep(0.3)
            p.progress((i + 1) / len(steps))

        st.success("Complete")
