"""Arc Concept Intelligence dashboard.

Decision workspace for comparing generated concepts, selecting a preferred option,
and exporting a concise AEC decision report.
"""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from modules.presentation import (
    concept_kpis,
    concepts_comparison_df,
    cost_breakdown_df,
    engineering_status_df,
    room_schedule_df,
    risk_matrix_df,
    sustainability_summary,
)
from modules.renderers import radar_chart
from modules.pdf_generator import generate_pdf_report
from modules.solar import compute_solar_potential
from modules.water import compute_water_harvesting
from modules.green_rating import compute_green_rating
from modules.aec_engine import compute_wind_load, compute_seismic_check
from modules.wind_detailed import compute_detailed_wind
from modules.seismic_advanced import compute_advanced_seismic

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
st.caption("Configure → Generate → Compare → Select → Analyse → Report")

concepts = st.session_state.get("generated_concepts") or []
if not concepts:
    st.info("Generate concepts from the Arc Concepts page first.")
    st.stop()

# Keep the selected concept stable across reruns and other dashboard actions.
previous = st.session_state.get("selected_concept_index", 0)
if not isinstance(previous, int) or previous < 0 or previous >= len(concepts):
    previous = 0

selected_index = st.selectbox(
    "Focus concept",
    range(len(concepts)),
    index=previous,
    format_func=lambda i: f"Concept {i + 1} · {concepts[i].get('type', 'AEC Concept')} · {concept_kpis(concepts[i])['Composite']}/100",
    key="concept_intelligence_selector",
)
st.session_state.selected_concept_index = selected_index
selected = concepts[selected_index]
st.session_state.active_design = selected
kpi = concept_kpis(selected)

# ---------------------------------------------------------
# Executive decision strip
# ---------------------------------------------------------
st.markdown("### Executive Summary")
k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Composite", f"{kpi['Composite']}/100")
k2.metric("Metric Design", f"{kpi['Metric Design']}/100")
k3.metric("GFA", f"{kpi['GFA (m²)']:,.1f} m²")
k4.metric("Cost", f"${kpi['Cost (USD)']:,.0f}")
k5.metric("Cost / m²", f"${kpi['Cost / m²']:,.0f}")
k6.metric("Carbon", f"{kpi['Embodied Carbon (tCO₂e)']:,.1f} t")

st.markdown("### Decision Snapshot")
ds1, ds2, ds3 = st.columns([1.2, 1, 1])
with ds1:
    st.markdown(
        f"**{selected.get('type', 'AEC Concept')}** · {selected.get('floors', 0)} floors · "
        f"{len(selected.get('rooms') or [])} programmed spaces · {selected.get('country', '')}"
    )
    st.write(f"**Soil:** {selected.get('soil_name', 'Not specified')}")
    st.write(f"**Planning engine:** {(selected.get('planning') or {}).get('planning_engine', 'metric-aware-v1')}")
with ds2:
    st.write(f"**Metric status:** {(selected.get('metric_design') or {}).get('status', 'REVIEW')}")
    st.write(f"**Metric checks:** {kpi['Metric Checks']}")
    st.write(f"**Space efficiency:** {kpi['Efficiency (%)']:.1f}%")
with ds3:
    st.write(f"**Site coverage:** {kpi['Site Coverage (%)']:.1f}%")
    st.write(f"**Spaces:** {kpi['Spaces']}")
    st.write(f"**Carbon / m²:** {kpi['Carbon / m²']:.1f} kgCO₂e/m²")

# ---------------------------------------------------------
# Comparison and intelligence profile
# ---------------------------------------------------------
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
    st.markdown("### Selection Rationale")
    scores = selected.get("scores") or {}
    score_items = {
        "Architecture": scores.get("arch", 0),
        "Structural": scores.get("struct", 0),
        "Sustainability": scores.get("sust", 0),
        "Cost": scores.get("cost", 0),
        "Metric Design": scores.get("metric", 0),
    }
    strongest = max(score_items, key=score_items.get)
    weakest = min(score_items, key=score_items.get)
    st.write(f"**Strongest dimension:** {strongest} ({score_items[strongest]}/100)")
    st.write(f"**Improvement priority:** {weakest} ({score_items[weakest]}/100)")
    st.write("**Recommendation:** Advance to detailed design only after project-specific engineering verification of the preliminary checks below.")

# ---------------------------------------------------------
# Cost and space intelligence
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# Engineering and sustainability gates
# ---------------------------------------------------------
st.markdown("### Engineering Gate")
engineering = engineering_status_df(selected)
st.dataframe(engineering, use_container_width=True, hide_index=True)

with st.expander("Engineering checks", expanded=False):
    ec = selected.get("eurocode") or {}
    st.write("**Eurocode ULS:**", ec.get("uls_status", "REVIEW"))
    st.write("**Wind:**", selected.get("wind", "Calculated in analysis view"))
    st.write("**Seismic:**", selected.get("seismic", "Calculated in analysis view"))
    try:
        wind = compute_wind_load(selected)
        detailed_wind = compute_detailed_wind(selected)
        seismic = compute_seismic_check(selected)
        advanced_seismic = compute_advanced_seismic(selected)
        wc1, wc2, wc3, wc4 = st.columns(4)
        wc1.metric("Wind pressure", f"{float(wind.get('wind_pressure', 0)):.2f} kN/m²")
        wc2.metric("Wind base shear", f"{float(detailed_wind.get('base_shear', 0)):.1f} kN")
        wc3.metric("Seismic zone", f"{float(seismic.get('seismic_zone', 0)):.2f}")
        wc4.metric("Seismic status", str(advanced_seismic.get("status", seismic.get("status", "REVIEW"))))
    except Exception as exc:
        st.warning(f"Advanced engineering summary unavailable: {exc}")

st.markdown("### Sustainability")
try:
    solar = compute_solar_potential(selected)
    water = compute_water_harvesting(selected)
    green = compute_green_rating(selected, selected.get("eurocode") or {})
    sust = sustainability_summary({**selected, "solar": solar, "water": water, "green_rating": green})
    s1, s2, s3, s4, s5 = st.columns(5)
    s1.metric("PV", f"{sust['PV (kWp)']:.1f} kWp")
    s2.metric("Annual energy", f"{sust['Annual Energy (kWh)']:,.0f} kWh")
    s3.metric("CO₂ savings", f"{sust['CO₂ Savings (t/yr)']:.1f} t/yr")
    s4.metric("Rainwater", f"{sust['Rainwater (m³/yr)']:,.1f} m³/yr")
    s5.metric("Green score", f"{sust['Green Score']:.0f}/100")
except Exception as exc:
    st.warning(f"Sustainability summary unavailable: {exc}")

# ---------------------------------------------------------
# Risk and report
# ---------------------------------------------------------
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

st.markdown("### Concept Intelligence Report")
st.caption("The report is a decision-stage summary. Engineering values remain preliminary until project-specific design inputs and professional verification are completed.")
report_col1, report_col2 = st.columns([1, 3])
with report_col1:
    generate_report = st.button("Generate PDF Report", type="primary", use_container_width=True)
if generate_report:
    try:
        solar = compute_solar_potential(selected)
        water = compute_water_harvesting(selected)
        green = compute_green_rating(selected, selected.get("eurocode") or {})
        wind = compute_wind_load(selected)
        seismic = compute_seismic_check(selected)
        boq = []
        for item in selected.get("boq_breakdown") or []:
            if isinstance(item, dict):
                boq.append({
                    "Item": item.get("Item", item.get("item", item.get("description", "Cost item"))),
                    "Qty": item.get("Qty", item.get("quantity", "-")),
                    "Total USD": item.get("Total USD", item.get("total_usd", item.get("cost", 0))),
                })
        pdf = generate_pdf_report(
            selected,
            selected.get("scores") or {},
            selected.get("eurocode") or {},
            selected.get("materials") or {},
            boq,
            selected.get("construction_schedule") or selected.get("schedule") or [],
            solar,
            water,
            green,
            wind,
            seismic,
        )
        st.download_button(
            "Download selected concept report",
            data=pdf.getvalue(),
            file_name=f"arc_concept_{selected_index + 1}_intelligence_report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
        st.success("Report generated for the selected concept.")
    except Exception as exc:
        st.error(f"Report generation failed: {exc}")

with st.expander("Raw AEC Data", expanded=False):
    st.json(selected)
