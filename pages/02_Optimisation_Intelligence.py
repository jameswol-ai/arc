"""Arc optimisation decision dashboard.

This page is intentionally isolated from the main Streamlit application so the
large concept renderer does not need to be rewritten just to expose optimiser
confidence metadata.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Arc | Optimisation Intelligence", page_icon="◈", layout="wide")

st.title("Optimisation Intelligence")
st.caption("Decision layer for cost-optimised AEC concepts")

concept = st.session_state.get("active_design")
if not concept:
    st.info("Generate or optimise a concept in Arc first.")
    st.stop()

opt = concept.get("optimisation") or {}
status = str(opt.get("status", "UNKNOWN")).upper()
confidence = str(opt.get("confidence", "UNKNOWN")).upper()
reason = opt.get("reason", "No optimisation explanation was recorded.")

if status == "VALID" and confidence == "HIGH":
    st.success("HIGH CONFIDENCE · VALID METRIC-PLANNED CANDIDATE")
elif status == "FALLBACK":
    st.warning("LOW CONFIDENCE · FALLBACK CANDIDATE")
else:
    st.info(f"OPTIMISATION STATUS · {status} · {confidence}")

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("Confidence", confidence)
with k2:
    st.metric("Status", status)
with k3:
    st.metric("Optimised Cost", f"${concept.get('total_usd', 0):,.0f}")
with k4:
    st.metric("Metric Score", f"{concept.get('metric_design', {}).get('score', 0):.0f}/100")

st.markdown("### Selection Rationale")
st.write(reason)

planning = concept.get("planning") or {}
metric = concept.get("metric_design") or {}

left, right = st.columns(2)
with left:
    st.markdown("### Planning Gate")
    planning_rows = {
        "Planning status": planning.get("status", status),
        "Planning engine": planning.get("planning_engine", "metric-aware-v1"),
        "Planning score": planning.get("metric_planning_score", concept.get("metric_planning_score", 0)),
        "Adjacency score": planning.get("adjacency_score", 0),
        "Program spaces": planning.get("room_program_count", len(concept.get("rooms", []))),
        "Bathrooms": planning.get("bathroom_count", 0),
    }
    st.dataframe(pd.DataFrame([planning_rows]), use_container_width=True, hide_index=True)

with right:
    st.markdown("### Engineering Gate")
    ec = concept.get("eurocode") or {}
    engineering_rows = {
        "Metric design": metric.get("status", "UNKNOWN"),
        "Metric score": metric.get("score", 0),
        "ULS status": ec.get("uls_status", "UNKNOWN"),
        "Structural span": concept.get("structural", {}).get("span", "n/a"),
        "Soil": concept.get("soil_name", "n/a"),
    }
    st.dataframe(pd.DataFrame([engineering_rows]), use_container_width=True, hide_index=True)

st.markdown("### Optimisation Metadata")
metadata = [
    {"Field": "Status", "Value": status},
    {"Field": "Confidence", "Value": confidence},
    {"Field": "Reason", "Value": reason},
    {"Field": "Candidate count", "Value": opt.get("candidate_count", opt.get("candidates", "n/a"))},
    {"Field": "Valid candidate count", "Value": opt.get("valid_candidate_count", "n/a")},
    {"Field": "Fallback candidate count", "Value": opt.get("fallback_candidate_count", "n/a")},
]
st.dataframe(pd.DataFrame(metadata), use_container_width=True, hide_index=True)

if status == "FALLBACK":
    st.warning(
        "This result is retained because no valid metric-planned candidate survived "
        "the optimisation gate. Treat it as a review candidate, not an approval."
    )

st.caption("Arc optimisation metadata is decision support. Final structural and code compliance requires project-specific engineering verification.")
