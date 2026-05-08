import streamlit as st
import matplotlib.pyplot as plt
import time

from floorplan_engine import FloorPlanEngine, building_to_dict

# =========================================================
# 🏗️ RANDOM LIVE BUILDING SIMULATOR
# =========================================================

st.set_page_config(page_title="Random AI - Living Architecture", layout="wide")

st.title("🏗️ Random AI — Living Building Generator")
st.caption("Watch structures grow like organisms forming spatial intelligence")

engine = FloorPlanEngine(grid_spacing=3.0)

# -----------------------------
# USER CONTROLS
# -----------------------------
col1, col2, col3 = st.columns(3)

with col1:
    building_type = st.selectbox("Building Type", ["residential", "commercial", "industrial"])

with col2:
    floors = st.slider("Floors", 1, 10, 3)

with col3:
    speed = st.slider("Growth Speed", 0.1, 1.5, 0.5)


# -----------------------------
# GENERATE MODEL
# -----------------------------
if st.button("🌱 Grow Building"):

    model = engine.generate_building(
        building_type=building_type,
        floors=floors,
        floor_width=25,
        floor_length=18
    )

    output = st.empty()

    # =========================================================
    # 🌿 LIVE GROWTH SIMULATION
    # =========================================================
    for f_index, floor in enumerate(model.floors):

        fig, ax = plt.subplots()

        ax.set_title(f"Floor {f_index + 1} — forming structure")
        ax.set_xlim(0, floor.width)
        ax.set_ylim(0, floor.length)

        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_aspect('equal')

        # draw rooms gradually (organic growth)
        for i, room in enumerate(floor.rooms):

            rect = plt.Rectangle(
                (room.x, room.y),
                room.width,
                room.length,
                fill=True,
                alpha=0.6
            )

            ax.add_patch(rect)

            ax.text(
                room.x + room.width / 2,
                room.y + room.length / 2,
                room.name,
                ha='center',
                va='center',
                fontsize=8
            )

            output.pyplot(fig)

            time.sleep(speed * 0.4)

        st.success(f"Floor {f_index + 1} stabilized")

    st.info("🏗️ Structure fully formed")

    # -----------------------------
    # FINAL FULL BUILDING VIEW
    # -----------------------------
    fig2, axes = plt.subplots(1, len(model.floors), figsize=(15, 5))

    if len(model.floors) == 1:
        axes = [axes]

    for idx, floor in enumerate(model.floors):

        ax = axes[idx]
        ax.set_title(f"Floor {idx + 1}")
        ax.set_xlim(0, floor.width)
        ax.set_ylim(0, floor.length)
        ax.set_xticks([])
        ax.set_yticks([])

        for room in floor.rooms:
            rect = plt.Rectangle(
                (room.x, room.y),
                room.width,
                room.length,
                alpha=0.7
            )
            ax.add_patch(rect)

    st.pyplot(fig2)

    # -----------------------------
    # EXPORT PREVIEW
    # -----------------------------
    st.subheader("🧾 Building Data Structure")
    st.json(building_to_dict(model))
