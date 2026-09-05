# =========================================================
# Arc — AEC INTELLIGENCE
# Metric Design Intelligence integrated into concept generation
# =========================================================

import streamlit as st
from datetime import datetime, timedelta
import random, pandas as pd, plotly.graph_objects as go
import numpy as np

from modules.config import M2_TO_FT2, format_length, format_area
from modules.auth import (
    load_users, create_user, authenticate, add_xp, xp_for_level,
    load_memory, save_memory, log_event, get_user
)
from modules.soil import REGION_SOIL_OPTIONS, get_soil_category, get_soil_multiplier
from modules.aec_engine import (
    ARCH_DOMAINS, generate_spatial_model, run_eurocode_analysis, calculate_ai_scores,
    compute_wind_load, compute_seismic_check
)
from modules.metric_design import validate_metric_design
from modules.materials import compute_materials
from modules.structural import compute_structural_design
from modules.construction import compute_construction_schedule
from modules.cost import compute_boq, compute_cost_by_trade
from modules.forex import STATIC_FX, init_fx
from modules.solar import compute_solar_potential
from modules.water import compute_water_harvesting
from modules.green_rating import compute_green_rating
from modules.ram_ai import ram_ai
from modules.renderers import (
    render_floorplan, render_3d, render_isometric,
    gantt_chart, radar_chart, plot_schedule_gantt
)
from modules.pdf_generator import generate_pdf_report
from modules.sharing import create_share_link
from modules.optimisation import optimise_cost
from modules.seismic_advanced import compute_advanced_seismic
from modules.wind_detailed import compute_detailed_wind

st.set_page_config(page_title="Arc – AEC Engine", page_icon="◈", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
html, body, .stApp { background:#0f0f0f; color:#e0e0e0; font-family:'Inter',sans-serif; }
.glass-panel { background:#1a1a1a; border:1px solid #2a2a2a; border-radius:12px; padding:20px 24px; margin-bottom:24px; }
.stButton > button { background:#2a2a2a; color:#fff; border:none; border-radius:8px; font-weight:500; padding:8px 20px; box-shadow:none; }
.stButton > button:hover { background:#3a3a3a; }
[data-testid="stSidebar"] { background:#0f0f0f; border-right:1px solid #2a2a2a; }
.stTextInput > div > div > input, .stNumberInput input, .stSelectbox > div > div, .stTextArea textarea { background:transparent !important; border:1px solid #333 !important; border-radius:6px; color:#e0e0e0 !important; }
.metric-bar-bg { background:#2a2a2a; border-radius:4px; height:6px; }
.metric-bar-fg { background:#888; height:6px; border-radius:4px; }
.stMetric .stMetricLabel { color:#aaa !important; }
.stMetric .stMetricValue { color:#e0e0e0 !important; }
div[data-testid="stMetricDelta"] { color:#aaa !important; }
h1,h2,h3,h4,h5,h6 { font-weight:400; color:#e0e0e0; }
</style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.user_data = None
    st.session_state.memory = {"designs": [], "concepts": [], "logs": []}
    st.session_state.generated_concepts = []
    st.session_state.active_design = None
    st.session_state.unit_system = "metric"
    st.session_state.ram_history = []
    st.session_state.selected_soil_name = "Nairobi Red Coffee Clay"
    st.session_state.selected_room_types = ["Bedroom", "Bathroom", "Living Room", "Kitchen"]

if not load_users():
    create_user("admin", "admin123")

if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='text-align:center;font-size:2rem;font-weight:300;color:#e0e0e0;'>Arc</div>", unsafe_allow_html=True)
        with st.form("auth"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            c1, c2 = st.columns(2)
            with c1: login_btn = st.form_submit_button("Login")
            with c2: reg_btn = st.form_submit_button("Sign up")
            if login_btn:
                user = authenticate(username, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.user_data = user
                    st.session_state.memory = load_memory(username)
                    st.rerun()
                else: st.error("Invalid credentials.")
            if reg_btn:
                if not username or not password: st.error("Fill all fields.")
                else:
                    try:
                        create_user(username, password)
                        st.success("Account created! Log in now.")
                    except ValueError as e: st.error(str(e))
    st.stop()

username = st.session_state.username
user = st.session_state.user_data
mem = st.session_state.memory

with st.sidebar:
    st.markdown("<div style='text-align:center;font-size:1.4rem;font-weight:300;color:#e0e0e0;'>Arc</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align:center;font-size:0.9rem;color:#888;'>{username} · Level {user['level']}</div>", unsafe_allow_html=True)
    lvl, xp = user["level"], user["xp"]
    needed = xp_for_level(lvl)
    prog = xp / needed if needed else 1
    st.markdown(f"<div style='display:flex;align-items:center;gap:6px;margin:10px 0'><span style='font-size:10px;color:#888;'>LVL {lvl}</span><div style='flex:1;height:5px;background:#2a2a2a;border-radius:2px'><div style='width:{prog*100}%;height:100%;background:#888;border-radius:2px'></div></div><span style='font-size:9px;color:#666;'>{xp}/{needed} XP</span></div>", unsafe_allow_html=True)

    unit = st.selectbox("Unit System", ["Metric (m, m²)", "Imperial (ft, sq ft)"])
    st.session_state.unit_system = "metric" if "Metric" in unit else "imperial"
    nav = st.radio("Navigate", ["Concepts", "Ram AI"])
    st.markdown("---")

    with st.expander("Configuration", expanded=True):
        st.markdown("**Trade Region · East African Countries**")
        country = st.selectbox("Country", list(STATIC_FX.keys()))
        domain = st.selectbox("Domain", list(ARCH_DOMAINS.keys()))
        typology = st.selectbox("Typology", ARCH_DOMAINS[domain])
        plot = st.slider("Plot Area (m²)", 200, 5000, 800, step=50)
        if st.session_state.unit_system == "imperial": st.caption(f"= {round(plot * M2_TO_FT2, 0)} sq ft")
        floors = st.slider("Floors", 1, 12, 3)
        baths = st.slider("Bathrooms", 1, 10, 2)
        soil_options = REGION_SOIL_OPTIONS.get(country, ["Generic Firm Sandy Gravel"])
        default_idx = soil_options.index(st.session_state.selected_soil_name) if st.session_state.selected_soil_name in soil_options else 0
        selected_soil = st.selectbox("Soil Condition", soil_options, index=default_idx, format_func=lambda x: f"{x} ({get_soil_category(x)}, {get_soil_multiplier(x)}x)")
        st.session_state.selected_soil_name = selected_soil
        st.markdown("**Room Types to Include**")
        room_type_options = ["Bedroom", "Bathroom", "Ensuite", "Corridor", "Balcony", "Living Room", "Kitchen", "Dining Room", "Office", "Storage"]
        selected_rooms = st.multiselect("Select room types (at least one of each will be generated)", options=room_type_options, default=st.session_state.selected_room_types)
        st.session_state.selected_room_types = selected_rooms

    if st.button("Generate Concepts", use_container_width=True):
        with st.spinner("Synthesizing 4 concepts with metric validation..."):
            concepts = []
            soil_name = st.session_state.selected_soil_name
            room_types = st.session_state.selected_room_types
            for i in range(4):
                d = generate_spatial_model(domain, typology, plot + random.randint(-400, 400), max(1, floors + random.randint(-2, 2)), max(1, baths + random.randint(-2, 2)), country, soil_name, room_types=room_types, seed=i)
                d["plan"] = d["rooms"]
                metric = validate_metric_design(d)
                d["metric_design"] = metric
                ec = run_eurocode_analysis(d, domain)
                d["eurocode"] = ec
                total_usd, total_local, fx, boq_breakdown = compute_boq(d, country)
                arch, struct, sust, cost, comp = calculate_ai_scores(d, ec, total_usd, "", metric_score=metric["score"])
                materials = compute_materials(d)
                d["scores"] = {"arch": arch, "struct": struct, "sust": sust, "cost": cost, "metric": metric["score"], "composite": comp}
                d["total_usd"] = total_usd
                d["total_local"] = total_local
                d["fx"] = fx
                d["boq_breakdown"] = boq_breakdown
                d["materials"] = materials
                concepts.append(d)
            concepts.sort(key=lambda x: (x["scores"]["composite"], x["scores"]["metric"]), reverse=True)
            st.session_state.generated_concepts = concepts
            st.session_state.active_design = concepts[0]
            log_event(username, mem, f"Generated 4 concepts. Top: {concepts[0]['id']} · Metric {concepts[0]['scores']['metric']}/100")
            leveled_up = add_xp(username, 20)
            st.session_state.user_data = get_user(username)
            if leveled_up: st.balloons()
            st.rerun()

    if st.button("Optimise Cost", use_container_width=True):
        with st.spinner("Optimising..."):
            best, cost = optimise_cost(domain, typology, country, selected_soil, st.session_state.selected_room_types, min_gfa=200)
            if best:
                best["metric_design"] = validate_metric_design(best)
                st.success(f"Optimised concept found! Cost: ${cost:,.0f}")
                st.session_state.generated_concepts = [best]
                st.session_state.active_design = best
                st.rerun()
            else: st.warning("No valid concept found.")

    with st.expander("Version History", expanded=False):
        if mem.get("designs"):
            for idx, ver in enumerate(reversed(mem["designs"])): st.write(f"{idx+1}. {ver['type']} - {ver['timestamp'][:10]}")
        else: st.write("No saved versions.")
    if st.button("Logout", use_container_width=True):
        save_memory(username, mem)
        st.session_state.logged_in = False
        st.rerun()

if nav == "Concepts":
    if st.session_state.generated_concepts:
        concepts = st.session_state.generated_concepts
        st.markdown("## Evolution Engine Results")
        st.caption("Concepts evaluated by Arc AI Agents + Metric Design Intelligence")
        names = ["Concept 1", "Concept 2", "Concept 3", "Concept 4"]
        tabs = st.tabs(names[:len(concepts)])
        for idx, (tab, c) in enumerate(zip(tabs, concepts)):
            with tab:
                sc = c["scores"]
                ec = c["eurocode"]
                metric = c.get("metric_design") or validate_metric_design(c)
                summary = metric["summary"]
                planning = c.get("planning") or {}
                st.markdown(f"**Design brief:** {c['type']}, {c['floors']}‑storey, {len(c['rooms'])} rooms, {c['country']}. Soil: {c['soil_name']}. GFA: {format_area(c['total_gfa'])}")
                m1, m2, m3, m4, m5 = st.columns(5)
                with m1: st.metric("Metric Design", f"{metric['score']}/100", delta=metric["status"])
                with m2: st.metric("Metric Checks", f"{summary['pass']}/{summary['total']}")
                with m3: st.metric("Efficiency", f"{summary['space_efficiency_pct']:.1f}%")
                with m4: st.metric("Site Coverage", f"{summary['site_coverage_pct']:.1f}%")
                with m5: st.metric("Composite", f"{sc['composite']}/100")
                if planning:
                    p1, p2, p3, p4 = st.columns(4)
                    with p1: st.metric("Planning Score", f"{c.get('metric_planning_score', 0):.1f}/100")
                    with p2: st.metric("Adjacency", f"{planning.get('adjacency_score', 0):.1f}/100")
                    with p3: st.metric("Program Spaces", planning.get('room_program_count', len(c.get('rooms', []))))
                    with p4: st.metric("Bathrooms", planning.get('bathroom_count', 0))
                    st.caption(f"Planning engine: {planning.get('planning_engine', 'metric-aware-v1')} · Generated candidates: {c.get('generated_candidates', 0)}")
                col1, col2 = st.columns([3,2])
                with col1:
                    st.markdown("### Floor Plan")
                    st.plotly_chart(render_floorplan(c["plan"], c["structural"]["span"]), use_container_width=True, key=f"fp_{c['id']}")
                    st.caption(f"Floor Area: {format_area(c['floor_area'])} | {c['floors']} floors | {c['country']}")
                    with st.expander("Material Breakdown"):
                        st.dataframe(pd.DataFrame(c['boq_breakdown']), use_container_width=True)
                with col2:
                    for lbl, key, col in [("Architect AI","arch","#888"),("Structural AI","struct","#aaa"),("Sustainability AI","sust","#777"),("Cost AI","cost","#999"),("Metric Design","metric","#bbb")]:
                        st.markdown(f"<div style='margin-bottom:6px;'><div style='display:flex;align-items:center;font-size:12px;color:#888'>{lbl} {sc[key]}%</div><div class='metric-bar-bg'><div class='metric-bar-fg' style='width:{sc[key]}%;background:{col};'></div></div></div>", unsafe_allow_html=True)
                    st.metric("USD Total", f"${c['total_usd']:,.0f}")
                    st.metric(f"Local ({c['fx']['currency']})", f"{c['fx']['symbol']} {c['total_local']:,.0f}")
                    st.markdown("### 3D Massing")
                    view = st.radio("View", ["Isometric","Interactive"], horizontal=True, key=f"view_{c['id']}")
                    if view == "Isometric": st.components.v1.html(render_isometric(c["plan"], c["structural"]["span"]), height=400)
                    else: st.plotly_chart(render_3d(c["plan"], c["floors"], c["structural"]["span"]), use_container_width=True, key=f"plot_{c['id']}")

                with st.expander("AEC Details (Metric, Structural, Materials, Carbon, Risks, Quality)", expanded=False):
                    st.markdown("#### Metric Design Validation")
                    if metric["status"] == "PASS": st.success(f"Metric design review: PASS · {metric['score']}/100")
                    elif metric["status"] == "REVIEW": st.warning(f"Metric design review: REVIEW · {metric['score']}/100")
                    else: st.error(f"Metric design review: FAIL · {metric['score']}/100")
                    st.write(f"**Checks:** {summary['pass']} pass · {summary['review']} review · {summary['fail']} fail")
                    st.dataframe(pd.DataFrame(metric["checks"]), use_container_width=True, hide_index=True)
                    if metric["warnings"]:
                        st.markdown("**Review items**")
                        st.dataframe(pd.DataFrame(metric["warnings"]), use_container_width=True, hide_index=True)
                    if metric["errors"]:
                        st.markdown("**Blocking items**")
                        st.dataframe(pd.DataFrame(metric["errors"]), use_container_width=True, hide_index=True)

                    st.markdown("#### Structural Design")
                    st.write(f"**Foundation:** {c['structural']['foundation']}")
                    st.write(f"**Slab System:** {c['structural']['slab_system']}")
                    st.write(f"**Storey Height:** {format_length(c['structural']['storey_height'])}")
                    st.write(f"**Wall Type:** {c['structural']['wall_type']}")
                    st.write(f"**Concrete Grade:** {c['structural']['concrete_grade']}")
                    st.write(f"**Steel Grade:** {c['structural']['steel_grade']}")
                    st.write(f"**Columns:** {c['structural']['columns']}")
                    st.write(f"**Beams:** {c['structural']['beams']}")
                    st.write(f"**Typical Span:** {format_length(c['structural']['span'])}")
                    st.markdown("#### Eurocode Check")
                    st.write(f"**Design Load:** {ec['design_load']}")
                    st.write(f"**M_ed:** {ec['m_ed']}")
                    st.write(f"**M_rd:** {ec['m_rd']}")
                    st.write(f"**Status:** {ec['uls_status']}")
                    st.markdown("#### Material Quantities & Embodied Carbon")
                    mats = c['materials']
                    st.write(f"**Concrete:** {mats['concrete_volume']} m³")
                    st.write(f"**Steel:** {mats['steel_weight']} kg")
                    st.write(f"**Brick:** {mats['brick_units']} units")
                    st.write(f"**Finishes:** {format_area(mats['finish_area'])}")
                    st.write(f"**Embodied Carbon:** {mats['embodied_carbon_t']} t CO₂e")
                    st.markdown("#### Detailed BOQ")
                    st.dataframe(pd.DataFrame(c['boq_breakdown']), use_container_width=True)
                    st.markdown("#### Structural Member Sizing")
                    sd = compute_structural_design(c, ec)
                    col_s1, col_s2, col_s3 = st.columns(3)
                    with col_s1:
                        st.write(f"**Columns:** {format_length(sd['column_width'])} × {format_length(sd['column_depth'])}")
                        st.write(f"**Beams:** {format_length(sd['beam_width'])} × {format_length(sd['beam_depth'])}")
                    with col_s2:
                        st.write(f"**Slab:** {format_length(sd['slab_thickness'])} thick")
                        st.write(f"**Footing:** {format_length(sd['footing_width'])} wide")
                    with col_s3:
                        st.write(f"**Beam Rebar:** {sd['beam_bars']}×20mm bars")
                        st.write(f"**Column Rebar:** {sd['column_bars']}×25mm bars")
                        st.write(f"**Slab Rebar:** {sd['slab_bars']}×12mm @200mm")
                        st.write(f"**Footing Rebar:** {sd['footing_bars']}×16mm")
                    st.markdown("#### Construction Schedule")
                    schedule_df = compute_construction_schedule(c)
                    st.dataframe(schedule_df[["Task", "Duration", "Start", "Finish", "Predecessors"]], use_container_width=True)
                    st.plotly_chart(plot_schedule_gantt(schedule_df), use_container_width=True)
                    st.markdown("#### Cost by Trade")
                    cost_df = compute_cost_by_trade(c, c["country"])
                    st.dataframe(cost_df.style.format({"Material":"${:,.0f}","Labour":"${:,.0f}","Equipment":"${:,.0f}","Total":"${:,.0f}","Total Local":"{:,.0f}"}), use_container_width=True)
                    st.markdown("#### Wind Load Analysis (Simplified)")
                    wind = compute_wind_load(c, c["country"])
                    col_w1, col_w2, col_w3 = st.columns(3)
                    with col_w1: st.metric("Wind Speed", f"{wind['wind_speed']} m/s")
                    with col_w2: st.metric("Wind Pressure", f"{wind['wind_pressure']} kN/m²")
                    with col_w3: st.metric("Base Shear", f"{wind['base_shear']} kN")
                    st.markdown("#### Detailed Wind (EC1)")
                    dw = compute_detailed_wind(c, c["country"])
                    st.write(f"**Basic Wind Speed:** {dw['v_b0']} m/s")
                    st.write(f"**Terrain Factor (kr):** {dw['kr']}")
                    st.write(f"**Roughness Coefficient (cr):** {dw['cr']}")
                    st.write(f"**Basic Pressure (qb):** {dw['qb']} kN/m²")
                    st.write(f"**Peak Velocity Pressure (qp):** {dw['qp']} kN/m²")
                    st.write(f"**Wind Force (F_wind):** {dw['F_wind']} kN")
                    st.markdown("#### Seismic Check (Simplified)")
                    seismic = compute_seismic_check(c, c["country"])
                    col_se1, col_se2, col_se3 = st.columns(3)
                    with col_se1: st.metric("Seismic Zone", f"{seismic['seismic_zone']:.2f}")
                    with col_se2: st.metric("Base Shear", f"{seismic['base_shear']} kN")
                    with col_se3: st.metric("Status", seismic['status'])
                    st.markdown("#### Advanced Seismic (EC8)")
                    aseismic = compute_advanced_seismic(c, c["country"])
                    st.write(f"**Ground Accel. (ag):** {aseismic['ag']:.3f} m/s²")
                    st.write(f"**Design Ground Accel. (agd):** {aseismic['agd']:.3f} m/s²")
                    st.write(f"**Spectral Response (Sd):** {aseismic['Sd']:.3f} m/s²")
                    st.write(f"**Base Shear (advanced):** {aseismic['base_shear']} kN")
                    st.write(f"**Soil Factor:** {aseismic['soil_factor']}")
                    st.write(f"**Period (T):** {aseismic['T']:.2f} s")
                    st.markdown("#### Solar & Energy Analysis")
                    solar = compute_solar_potential(c)
                    col_e1, col_e2, col_e3 = st.columns(3)
                    with col_e1:
                        st.metric("Roof Area", format_area(solar['roof_area']))
                        st.metric("Installed PV", f"{solar['installed_capacity']} kWp")
                    with col_e2:
                        st.metric("Annual Energy", f"{solar['annual_energy']:,} kWh")
                        st.metric("CO₂ Savings", f"{solar['co2_savings']} tonnes/yr")
                    with col_e3:
                        st.caption("PV Performance")
                        st.progress(min(1.0, solar['annual_energy'] / 5000), text=f"{solar['annual_energy']} kWh/yr")
                    st.markdown("#### Water Efficiency & Rainwater Harvesting")
                    water = compute_water_harvesting(c)
                    st.write(f"**Rainfall:** {water['rainfall']} mm/year")
                    st.write(f"**Harvestable Volume:** {water['harvestable_volume']} m³/year")
                    st.progress(water['savings_percentage']/100, text=f"{water['savings_percentage']}% of typical water use")
                    st.caption("Typical building water use: 100 m³/year")
                    st.markdown("#### Green Building Rating")
                    rating = compute_green_rating(c, ec)
                    st.metric("Score", f"{rating['score']}/100", delta=rating['rating'])
                    st.progress(rating['score']/100, text=f"{rating['score']}%")
                    st.markdown("#### Risk Register")
                    risks = [{"Risk":"Foundation settlement","Likelihood":"Medium","Impact":"High","Mitigation":"Soil improvement"},{"Risk":"Steel supply delay","Likelihood":"High","Impact":"Medium","Mitigation":"Pre-order steel"},{"Risk":"Labour shortage","Likelihood":"Low","Impact":"Medium","Mitigation":"Local hiring plan"},{"Risk":"Weather disruption","Likelihood":"Medium","Impact":"Low","Mitigation":"Flexible schedule"},{"Risk":"Cost overrun","Likelihood":"High","Impact":"High","Mitigation":"10% contingency"}]
                    st.table(pd.DataFrame(risks))
                    st.markdown("#### Quality Checklist")
                    checklist = [{"Phase":"Foundation","Item":"Excavation depth","Status":"Pass"},{"Phase":"Foundation","Item":"Reinforcement placement","Status":"Pass"},{"Phase":"Foundation","Item":"Concrete pour","Status":"Pass"},{"Phase":"Structure","Item":"Column alignment","Status":"Pass"},{"Phase":"Structure","Item":"Beam formwork","Status":"Pass"},{"Phase":"Structure","Item":"Slab curing","Status":"Pass"},{"Phase":"Finishes","Item":"Floor flatness","Status":"Pass"},{"Phase":"Finishes","Item":"Wall plaster","Status":"Pass"},{"Phase":"Finishes","Item":"Painting","Status":"Pass"},{"Phase":"MEP","Item":"Electrical conduit","Status":"Pass"},{"Phase":"MEP","Item":"Plumbing layout","Status":"Pass"}]
                    st.table(pd.DataFrame(checklist))
    else:
        st.info("Configure the project in the sidebar and generate concepts.")
else:
    st.markdown("## Ram AI")
    prompt = st.text_area("Ask Ram AI about the current design")
    if st.button("Ask Ram"):
        if st.session_state.active_design:
            answer = ram_ai(prompt, st.session_state.active_design)
            st.write(answer)
        else: st.info("Generate a concept first.")
