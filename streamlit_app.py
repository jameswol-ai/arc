import streamlit as st
import numpy as np
import time
import random
import matplotlib.pyplot as plt

# =========================================================
# 🧠 RANDOM AI — CONTROL CENTER DASHBOARD
# Architecture + Structure + MEP + Cost + Export
# =========================================================

if mode == "Export Center":
    st.header("🏗️ BIM Digital Twin Viewer")

    if st.button("Generate BIM Model"):
        result = run_pipeline(intent_text, site_area)

        bim = result["bim"]

        st.write("### BIM ELEMENT COUNT")
        st.metric("Elements", len(bim.elements))

        st.write("### SAMPLE ELEMENT")
        sample_id = list(bim.elements.keys())[0]
        st.json(bim.get_element(sample_id).__dict__)

        st.download_button(
            "Download BIM JSON",
            data=export_bim(bim),
            file_name="bim_model.json"
        )

st.set_page_config(page_title="Random AI Control Center", layout="wide")

# =========================
# HEADER
# =========================
st.title("🏗️ RANDOM AI — CONTROL CENTER")
st.caption("A generative architecture + structural intelligence system")

# =========================
# SIDEBAR NAVIGATION
# =========================
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
        "Full Pipeline Simulation"
    ]
)

# =========================================================
# AI BRAIN MODULE
# =========================================================
st.subheader("🧬 Evolution Output")
st.json(result["current_design"]["score"])

st.subheader("🧠 Next Generation Seed")
st.json(result["next_generation_seed"])

from core.pipeline import run_pipeline

if mode == "AI Brain":
    st.header("🧠 Design Brain + Full System Pipeline")

    intent_text = st.text_area("Describe building")

    site_area = st.number_input("Site Area (m²)", value=1000.0)

    if st.button("RUN FULL BUILDING GENERATION"):
        result = run_pipeline(intent_text, site_area)

        st.success("Pipeline executed")

        st.subheader("AI INTENT")
        st.json(result["intent"])

        st.subheader("ARCHITECTURE")
        st.json(result["architecture"])

        st.subheader("STRUCTURE")
        st.json(result["structure"])

if mode == "AI Brain":
    st.header("🧠 Design Brain")

    intent = st.text_area("Describe your building intent")

    if st.button("Generate Concept"):
        st.success("AI is interpreting architectural intent...")

        st.write("### Concept Output")
        st.json({
            "building_type": random.choice(["Residential", "Commercial", "Industrial"]),
            "style": random.choice(["Modern", "Brutalist", "Organic", "Parametric"]),
            "efficiency_score": round(random.uniform(0.6, 0.95), 2),
            "structural_complexity": random.choice(["Low", "Medium", "High"])
        })

# =========================================================
# ARCHITECTURE MODULE
# =========================================================
elif mode == "Architecture Generator":
    st.header("🏛️ Architecture Engine")

    floors = st.slider("Number of Floors", 1, 50, 5)
    building_type = st.selectbox("Type", ["Residential", "Commercial", "Industrial"])

    if st.button("Generate Floorplan"):
        st.success("Generating floor system...")

        for i in range(floors):
            st.write(f"Floor {i+1}: Grid-based layout generated")

        st.info("Zoning rules applied + circulation paths optimized")

# =========================================================
# STRUCTURE ENGINE
# =========================================================
from structure.eurocode_engine import structural_assessment

if mode == "Structure Engine":
    st.header("🏗️ Eurocode Structural Analysis")

    span = st.slider("Beam Span (m)", 2.0, 12.0, 6.0)
    floors = st.slider("Floors", 1, 20, 5)
    area = st.number_input("Floor Area (m²)", value=500.0)
    height = st.slider("Column Height (m)", 2.5, 6.0, 3.2)

    if st.button("Run Eurocode Check"):
        result = structural_assessment(span, area, area * 0.6, height)

        st.subheader("Results")

        st.write("ULS Load:", result["ULS_load_kN"])

        st.write("### Beam Check")
        st.json(result["beam_check"])

        st.write("### Column Check")
        st.json(result["column_check"])

        if result["global_safe"]:
            st.success("Structure passes simplified Eurocode checks")
        else:
            st.error("Structural failure risk detected")

elif mode == "Structure Engine":
    st.header("🏗️ Structural System (Eurocode Logic)")

    load = st.number_input("Applied Load (kN)", value=10.0)

    if st.button("Run Structural Analysis"):
        stress = load * random.uniform(1.2, 2.5)
        safety_factor = random.uniform(1.5, 3.0)

        st.write("### Results")
        st.metric("Stress Level", f"{stress:.2f} kN/m²")
        st.metric("Safety Factor", f"{safety_factor:.2f}")

        if safety_factor > 2:
            st.success("Structure is SAFE under Eurocode-like assumptions")
        else:
            st.error("WARNING: Structural redesign required")

# =========================================================
# MEP SYSTEMS
# =========================================================
elif mode == "MEP Systems":
    st.header("⚡ Mechanical, Electrical, Plumbing")

    st.write("Simulating building services layout...")

    hvac_efficiency = random.randint(70, 98)
    water_flow = random.randint(60, 100)
    power_load = random.randint(50, 120)

    st.metric("HVAC Efficiency", f"{hvac_efficiency}%")
    st.metric("Water System Flow", f"{water_flow} L/s")
    st.metric("Electrical Load", f"{power_load} kW")

# =========================================================
# GIS MODULE
# =========================================================
elif mode == "GIS & Site":
    st.header("🌍 Site & Terrain Intelligence")

    slope = random.uniform(0, 35)

    st.write(f"Site slope: {slope:.2f}°")

    fig, ax = plt.subplots()
    x = np.linspace(0, 10, 100)
    y = np.sin(x) + slope / 10

    ax.plot(x, y)
    ax.set_title("Terrain Profile")
    st.pyplot(fig)

# =========================================================
# COST ENGINE
# =========================================================
elif mode == "Cost Engine":
    st.header("💰 Construction Cost Simulation")

    area = st.number_input("Floor Area (m²)", value=500)

    cost_per_m2 = random.randint(400, 1200)
    total_cost = area * cost_per_m2

    st.metric("Cost per m²", f"${cost_per_m2}")
    st.metric("Total Estimated Cost", f"${total_cost:,.0f}")

# =========================================================
# RENDERING
# =========================================================
elif mode == "Rendering":
    st.header("🧊 Massing & Visualization")

    size = st.slider("Building Mass Size", 1, 10, 5)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    x = np.random.rand(50) * size
    y = np.random.rand(50) * size
    z = np.random.rand(50) * size

    ax.scatter(x, y, z)
    st.pyplot(fig)

# =========================================================
# EXPORT CENTER
# =========================================================
elif mode == "Export Center":
    st.header("📦 BIM Export Hub")

    st.write("Export formats ready:")

    st.checkbox("DXF")
    st.checkbox("IFC")
    st.checkbox("PDF Report")
    st.checkbox("Construction Schedule")

    if st.button("Export Project"):
        st.success("Project exported successfully (simulated)")

# =========================================================
# FULL PIPELINE SIMULATION
# =========================================================
elif mode == "Full Pipeline Simulation":
    st.header("🚀 End-to-End System Run")

    if st.button("Run Full Simulation"):
        steps = [
            "AI Brain interpreting intent",
            "Generating architecture",
            "Calculating structural system",
            "Integrating MEP systems",
            "Evaluating cost",
            "Rendering massing model",
            "Exporting BIM package"
        ]

        progress = st.progress(0)

        for i, step in enumerate(steps):
            st.write(step)
            time.sleep(0.6)
            progress.progress((i + 1) / len(steps))

        st.success("Simulation complete — building system generated")

     #Parametric BIM Control#
elif mode == "Parametric BIM":

    st.header("🧬 Parametric BIM Control System")

    result = run_pipeline(intent_text, site_area)
    engine = result["parametric_engine"]
    bim = result["bim"]

    st.subheader("⚙️ Parameters")

    floor_height = st.slider("Floor Height", 2.5, 5.0, 3.2)
    grid_spacing = st.slider("Grid Spacing", 3.0, 8.0, 4.0)
    wall_thickness = st.slider("Wall Thickness", 0.1, 0.5, 0.2)

    if st.button("Update Model"):
        engine.set_parameter("floor_height", floor_height)
        engine.set_parameter("grid_spacing", grid_spacing)
        engine.set_parameter("wall_thickness", wall_thickness)

        updated = engine.get_model()

        st.success("BIM model updated parametrically")

        st.metric("Elements", len(updated.elements))

        sample = list(updated.elements.values())[0]
        st.json(sample.__dict__)
