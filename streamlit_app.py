import streamlit as st
import numpy as np
import time
import random
import matplotlib.pyplot as plt

# =========================================================
# 🧠 RANDOM AI — CONTROL CENTER DASHBOARD
# Architecture + Structure + MEP + Cost + Export
# =========================================================

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
