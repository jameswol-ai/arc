"""Arc Concept Intelligence dashboard.

This page presents generated concepts as a decision workspace while keeping
engineering calculations and raw detail in the existing Concepts view.
"""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from modules.presentation import (
    concepts_comparison_df,
    concept_kpis,
    cost_breakdown_df,
    engineering_status_df,
    room_schedule_df,
    risk_matrix_df,
)
from modules.renderers import radar_chart
from modules.config import format_area

st.set_page_config(page_title="Arc · Concept Intelligence", page_icon="◈", layout="wide")

st.markdown(
    """
    <style>
    .arc-card {background:#151515;border:1px solid #2b2b2b;border-radius:12px;padding:16px 18px;margin-bottom:12px;}
    .arc-muted {color:#8b8b8b;font-size:.86rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Concept Intelligence")
st.caption("A decision layer for architecture, engineering, cost and sustainability.")

concepts = st.session_state.get("generated_concepts") or []
if not concepts:
    st.info("Generate concepts from the Arc Concepts page first.")
    st.stop()

selected_index = st.selectbox(
    "Focus concept",
    range(len(concepts)),
    format_func=lambda i: f"Concept {i + 1} · {concepts[i].get('type', 'AEC Concept')}",
)
selected = concepts[selected_index]
kpi = concept_kpis(selected)

st.markdown("### Executive Summary")
k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Composite", f"{kpi['Composite']}/100")
k2.metric("Metric Design", f"{kpi['Metric Design']}/100")
k3.metric("GFA", f"{kpi['GFA (m²)']:,.1f} m²")
k4.metric("Cost", f"${kpi['Cost (USD)']:,.0f}")
k5.metric("Cost / m²", f"${kpi['Cost / m²']:,.0f}")
k6.metric("Carbon", f"{kpi['Embodied Carbon (tCO₂e)']:,.1f} t")

st.markdown("### Concept Comparison")
comparison = concepts_comparison_df(concepts)
if not comparison.empty:
    st.dataframe(
        comparison,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Rank": st.column_config.NumberColumn("Rank", format="%d"),
            "Composite": st.column_config.ProgressColumn("Composite", min_value=0, max_value=100, format="%d"),
            "Metric Design": st.column_config.ProgressColumn("Metric Design", min_value=0, max_value=100, format="%d"),
            "Architecture": st.column_config.NumberColumn("Architecture", format="%d"),
            "Structural": st.column_config.NumberColumn("Structural", format="%d"),
            "Sustainability": st.column_config.NumberColumn("Sustainability", format="%d"),
            "Cost AI": st.column_config.NumberColumn("Cost AI", format="%d"),
            "GFA (m²)": st.column_config.NumberColumn("GFA (m²)", format="%.1f"),
            "Cost (USD)": st.column_config.NumberColumn("Cost (USD)", format="$%0.0f"),
            "Cost / m²": st.column_config.NumberColumn("Cost / m²", format="$%0.0f"),
            "Embodied Carbon (tCO₂e)": st.column_config.NumberColumn("Embodied Carbon (tCO₂e)", format="%.1f"),
            "Carbon / m²": st.column_config.NumberColumn("Carbon / m²", format="%.1f"),
        },
    )

left, right = st.columns([1, 1])
with left:
    st.markdown("### Intelligence Profile")
    st.plotly_chart(
        radar_chart(selected["scores"]),
        use_container_width=True,
        key=f"intel_radar_{selected.get('id', selected_index)}",
    )
with right:
    st.markdown("### Decision Snapshot")
    st.markdown(
        f"**{selected.get('type', 'AEC Concept')}** · {selected.get('floors', 0)} floors · "
        f"{len(selected.get('rooms') or [])} programmed spaces · {selected.get('country', '')}"
    )
    st.write(f"**Metric status:** {(selected.get('metric_design') or {}).get('status', 'REVIEW')}")
    st.write(f"**Metric checks:** {kpi['Metric Checks']}")
    st.write(f"**Space efficiency:** {kpi['Efficiency (%)']:.1f}%")
    st.write(f"**Site coverage:** {kpi['Site Coverage (%)']:.1f}%")
    st.write(f"**Soil:** {selected.get('soil_name', 'Not specified')}")
    st.write(f"**Planning engine:** {(selected.get('planning') or {}).get('planning_engine', 'metric-aware-v1')}")

st.markdown("### Cost Intelligence")
cost_df = cost_breakdown_df(selected)
if not cost_df.empty:
    cc1, cc2 = st.columns([2, 1])
    with cc1:
        fig = px.bar(cost_df.head(10), x="Cost (USD)", y="Item", orientation="h", text="Share (%)")
        fig.update_layout(height=430, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True, key=f"cost_{selected_index}")
    with cc2:
        st.dataframe(cost_df, use_container_width=True, hide_index=True)
else:
    st.info("No detailed cost breakdown is available for this concept.")

st.markdown("### Space Programme")
rooms = room_schedule_df(selected)
if not rooms.empty:
    rc1, rc2 = st.columns([1, 2])
    with rc1:
        area_by_type = rooms.groupby("Type", as_index=False)["Area (m²)"].sum().sort_values("Area (m²)", ascending=False)
        fig = px.bar(area_by_type, x="Area (m²)", y="Type", orientation="h")
        fig.update_layout(height=430, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True, key=f"areas_{selected_index}")
    with rc2:
        st.dataframe(rooms, use_container_width=True, hide_index=True)

st.markdown("### Engineering Gate")
engineering = engineering_status_df(selected)
st.dataframe(engineering, use_container_width=True, hide_index=True)

st.markdown("### Risk Matrix")
risks = risk_matrix_df()
risk_left, risk_right = st.columns([2, 1])
with risk_left:
    likelihood = {"Low": 1, "Medium": 2, "High": 3}
    impact = {"Low": 1, "Medium": 2, "High": 3}
    risk_plot = risks.copy()
    risk_plot["Likelihood Score"] = risk_plot["Likelihood"].map(likelihood)
    risk_plot["Impact Score"] = risk_plot["Impact"].map(impact)
    fig = px.scatter(
        risk_plot,
        x="Likelihood Score",
        y="Impact Score",
        size="Score",
        hover_name="Risk",
        hover_data=["Mitigation", "Score"],
        text="Risk",
    )
    fig.update_xaxes(tickvals=[1, 2, 3], ticktext=["Low", "Medium", "High"], range=[0.5, 3.5])
    fig.update_yaxes(tickvals=[1, 2, 3], ticktext=["Low", "Medium", "High"], range=[0.5, 3.5])
    fig.update_layout(height=430, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True, key=f"risks_{selected_index}")
with risk_right:
    st.dataframe(risks, use_container_width=True, hide_index=True)

st.markdown("### Raw AEC Data")
with st.expander("Concept dictionary", expanded=False):
    st.json(selected)
