"""Presentation helpers for Arc concept intelligence dashboards.

This module deliberately contains no Streamlit calls. It normalises generated
concept dictionaries into stable, presentation-ready tables and KPI records.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List

import pandas as pd


def _num(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def concept_kpis(concept: Dict[str, Any]) -> Dict[str, Any]:
    """Return a compact executive KPI record for one concept."""
    scores = concept.get("scores") or {}
    metric = concept.get("metric_design") or {}
    summary = metric.get("summary") or {}
    materials = concept.get("materials") or {}
    gfa = _num(concept.get("total_gfa"))
    cost = _num(concept.get("total_usd"))
    carbon = _num(materials.get("embodied_carbon_t"))

    return {
        "Composite": round(_num(scores.get("composite"))),
        "Metric Design": round(_num(scores.get("metric"))),
        "Architecture": round(_num(scores.get("arch"))),
        "Structural": round(_num(scores.get("struct"))),
        "Sustainability": round(_num(scores.get("sust"))),
        "Cost AI": round(_num(scores.get("cost"))),
        "GFA (m²)": round(gfa, 1),
        "Cost (USD)": round(cost, 0),
        "Cost / m²": round(cost / gfa, 2) if gfa > 0 else 0.0,
        "Embodied Carbon (tCO₂e)": round(carbon, 2),
        "Carbon / m²": round(carbon * 1000 / gfa, 2) if gfa > 0 else 0.0,
        "Metric Checks": f"{summary.get('pass', 0)}/{summary.get('total', 0)}",
        "Efficiency (%)": round(_num(summary.get("space_efficiency_pct")), 1),
        "Site Coverage (%)": round(_num(summary.get("site_coverage_pct")), 1),
        "Floors": int(_num(concept.get("floors"))),
        "Spaces": len(concept.get("rooms") or []),
    }


def concepts_comparison_df(concepts: Iterable[Dict[str, Any]]) -> pd.DataFrame:
    """Build a ranked concept comparison matrix."""
    rows: List[Dict[str, Any]] = []
    for index, concept in enumerate(concepts, start=1):
        row = concept_kpis(concept)
        row["Rank"] = index
        row["Concept"] = f"Concept {index}"
        row["Type"] = concept.get("type", "Unknown")
        rows.append(row)

    if not rows:
        return pd.DataFrame()

    columns = [
        "Rank", "Concept", "Type", "Composite", "Metric Design",
        "Architecture", "Structural", "Sustainability", "Cost AI",
        "GFA (m²)", "Cost (USD)", "Cost / m²", "Embodied Carbon (tCO₂e)",
        "Carbon / m²", "Metric Checks", "Efficiency (%)", "Site Coverage (%)",
        "Floors", "Spaces",
    ]
    return pd.DataFrame(rows).reindex(columns=columns)


def room_schedule_df(concept: Dict[str, Any]) -> pd.DataFrame:
    """Return a clean room schedule with dimensions and areas."""
    rows: List[Dict[str, Any]] = []
    for index, room in enumerate(concept.get("rooms") or [], start=1):
        width = _num(room.get("w", room.get("width")))
        depth = _num(room.get("h", room.get("depth")))
        area = _num(room.get("area"), width * depth)
        rows.append({
            "No.": index,
            "Space": room.get("name") or room.get("type") or f"Space {index}",
            "Type": room.get("type", "Other"),
            "Floor": room.get("floor", 1),
            "Width (m)": round(width, 2),
            "Depth (m)": round(depth, 2),
            "Area (m²)": round(area, 2),
        })
    return pd.DataFrame(rows)


def cost_breakdown_df(concept: Dict[str, Any]) -> pd.DataFrame:
    """Normalise the detailed BOQ into a compact cost table."""
    raw = concept.get("boq_breakdown") or []
    if not raw:
        return pd.DataFrame(columns=["Item", "Cost (USD)", "Share (%)"])

    rows: List[Dict[str, Any]] = []
    total = _num(concept.get("total_usd"))
    for item in raw:
        if not isinstance(item, dict):
            continue
        name = item.get("item") or item.get("description") or item.get("name") or "Cost item"
        value = item.get("total_usd", item.get("cost", item.get("amount", 0)))
        value = _num(value)
        rows.append({
            "Item": name,
            "Cost (USD)": round(value, 2),
            "Share (%)": round(value * 100 / total, 1) if total > 0 else 0.0,
        })
    return pd.DataFrame(rows).sort_values("Cost (USD)", ascending=False).reset_index(drop=True)


def engineering_status_df(concept: Dict[str, Any]) -> pd.DataFrame:
    """Summarise major engineering checks without hiding the raw results."""
    metric = concept.get("metric_design") or {}
    eurocode = concept.get("eurocode") or {}
    rows = [
        {"Check": "Metric Design", "Status": metric.get("status", "REVIEW"), "Score": _num(metric.get("score"))},
        {"Check": "Eurocode ULS", "Status": eurocode.get("uls_status", "REVIEW"), "Score": None},
    ]
    return pd.DataFrame(rows)


def sustainability_summary(concept: Dict[str, Any]) -> Dict[str, Any]:
    """Extract the sustainability metrics used by the dashboard."""
    return {
        "PV (kWp)": _num((concept.get("solar") or {}).get("installed_capacity")),
        "Annual Energy (kWh)": _num((concept.get("solar") or {}).get("annual_energy")),
        "CO₂ Savings (t/yr)": _num((concept.get("solar") or {}).get("co2_savings")),
        "Rainwater (m³/yr)": _num((concept.get("water") or {}).get("harvestable_volume")),
        "Green Score": _num((concept.get("green_rating") or {}).get("score")),
    }


def risk_matrix_df() -> pd.DataFrame:
    """Default project risk register used by the presentation layer."""
    return pd.DataFrame([
        {"Risk": "Foundation settlement", "Likelihood": "Medium", "Impact": "High", "Score": 6, "Mitigation": "Soil improvement / verify geotechnical design"},
        {"Risk": "Steel supply delay", "Likelihood": "High", "Impact": "Medium", "Score": 6, "Mitigation": "Early procurement and approved alternatives"},
        {"Risk": "Labour shortage", "Likelihood": "Low", "Impact": "Medium", "Score": 3, "Mitigation": "Local hiring and subcontractor plan"},
        {"Risk": "Weather disruption", "Likelihood": "Medium", "Impact": "Low", "Score": 2, "Mitigation": "Weather-aware construction programme"},
        {"Risk": "Cost overrun", "Likelihood": "High", "Impact": "High", "Score": 9, "Mitigation": "Cost control, procurement strategy and contingency"},
    ])


def quality_summary_df(checklist: Iterable[Dict[str, Any]]) -> pd.DataFrame:
    """Aggregate a quality checklist into status counts."""
    df = pd.DataFrame(list(checklist))
    if df.empty or "Status" not in df.columns:
        return pd.DataFrame(columns=["Status", "Count"])
    return df.groupby("Status", dropna=False).size().reset_index(name="Count")
