import streamlit as st
from datetime import datetime, timedelta
import random, pandas as pd, plotly.graph_objects as go

# ─── Import from modules ──────────────────────────────────────
from modules.config import M2_TO_FT2, to_display_length, to_display_area, format_length, format_area
from modules.auth import (
    load_users, create_user, authenticate, add_xp, xp_for_level,
    load_memory, save_memory, log_event, get_user
)
from modules.soil import SOIL_TYPES, REGION_SOIL_OPTIONS, get_soil_category, get_soil_multiplier
from modules.aec_engine import (
    ARCH_DOMAINS, generate_spatial_model, run_eurocode_analysis, calculate_ai_scores
)
from modules.materials import compute_materials
from modules.structural import compute_structural_design
from modules.construction import compute_construction_schedule
from modules.cost import compute_boq, compute_cost_by_trade
from modules.forex import (
    STATIC_FX, init_fx, get_fx, get_all_countries, convert_currency,
    fetch_hist, plot_hist, forest, _CURRENT_RATES, _BASELINE_RATES
)
from modules.solar import compute_solar_potential
from modules.water import compute_water_harvesting
from modules.green_rating import compute_green_rating
from modules.ram_ai import ram_ai
from modules.renderers import (
    render_floorplan, render_3d, render_isometric,
    gantt_chart, radar_chart, plot_schedule_gantt
)

# ─── Page config ──────────────────────────────────────────────
st.set_page_config(page_title="Arc – AEC Engine", page_icon="◈", layout="wide")

# ─── Custom CSS (unchanged) ──────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html,body,.stApp{background:#0a0a0a;color:#cccccc;font-family:'Inter',sans-serif}
.glass-panel{background:#111111;border:1px solid #333333;border-radius:18px;padding:20px}
.stButton>button{background:#333333;color:#ffffff;border:none;border-radius:10px;font-weight:600;padding:8px 20px;transition:all .2s;box-shadow:0 2px 8px rgba(0,0,0,0.5)}
.stButton>button:hover{background:#444444;box-shadow:0 4px 12px rgba(0,0,0,0.8)}
[data-testid="stSidebar"]{background:#0a0a0a;border-right:1px solid #222}
.stTextInput>div>div>input,.stNumberInput input,.stSelectbox>div>div,.stTextArea textarea{background:transparent!important;border:1px solid #333!important;border-radius:8px;color:#cccccc!important}
.metric-bar-bg{background:#222;border-radius:5px;height:6px}
.metric-bar-fg{border-radius:5px;background:#888;height:6px}
.stMetric .stMetricLabel{color:#aaaaaa!important}
.stMetric .stMetricValue{color:#cccccc!important}
div[data-testid="stMetricDelta"]{color:#aaaaaa!important}
</style>
""", unsafe_allow_html=True)

# ─── Session initialisation ──────────────────────────────────
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

# Ensure at least one admin user exists
if not load_users():
    create_user("admin", "admin123")

# ─── LOGIN ────────────────────────────────────────────────────
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='text-align:center;font-size:2rem;font-weight:300;color:#aaaaaa;'>◈ Arc</div>", unsafe_allow_html=True)
        with st.form("auth"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            c1, c2 = st.columns(2)
            with c1:
                login_btn = st.form_submit_button("Login")
            with c2:
                reg_btn = st.form_submit_button("Sign up")

            if login_btn:
                user = authenticate(username, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.user_data = user
                    st.session_state.memory = load_memory(username)
                    st.rerun()
                else:
                    st.error("Invalid credentials.")
            if reg_btn:
                if not username or not password:
                    st.error("Fill all fields.")
                else:
                    try:
                        create_user(username, password)
                        st.success("Account created! Log in now.")
                    except ValueError as e:
                        st.error(str(e))
    st.stop()

# ─── SIDEBAR ──────────────────────────────────────────────────
username = st.session_state.username
user = st.session_state.user_data
mem = st.session_state.memory

with st.sidebar:
    st.markdown("<div style='text-align:center;font-size:1.4rem;font-weight:300;color:#aaaaaa;'>◈ Arc</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align:center;font-size:0.9rem;color:#888;'>{username} · Lvl {user['level']}</div>", unsafe_allow_html=True)

    lvl, xp = user["level"], user["xp"]
    needed = xp_for_level(lvl)
    prog = xp / needed if needed else 1
    st.markdown(f"""
    <div style='display:flex;align-items:center;gap:6px;margin:10px 0'>
      <span style='font-size:10px;color:#888;'>LVL {lvl}</span>
      <div style='flex:1;height:5px;background:#222;border-radius:2px'>
        <div style='width:{prog*100}%;height:100%;background:#888;border-radius:2px'></div>
      </div>
      <span style='font-size:9px;color:#666;'>{xp}/{needed} XP</span>
    </div>
    """, unsafe_allow_html=True)

    unit = st.selectbox("📏 Unit System", ["Metric (m, m²)", "Imperial (ft, sq ft)"])
    st.session_state.unit_system = "metric" if "Metric" in unit else "imperial"
    nav = st.radio("Navigate", ["Dashboard", "Concepts", "Ram AI"])
    st.markdown("---")

    # ─── Configuration expander ──────────────────────────────
    with st.expander("📐 Arc Configuration", expanded=True):
        st.markdown("**Trade Region · East African Countries**")
        country = st.selectbox("Country", list(STATIC_FX.keys()))
        domain = st.selectbox("Domain", list(ARCH_DOMAINS.keys()))
        typology = st.selectbox("Typology", ARCH_DOMAINS[domain])
        plot = st.slider("Plot Area (m²)", 200, 5000, 800, step=50)
        if st.session_state.unit_system == "imperial":
            st.caption(f"= {round(plot * M2_TO_FT2, 0)} sq ft")
        floors = st.slider("Floors", 1, 12, 3)
        baths = st.slider("Bathrooms", 1, 10, 2)

        soil_options = REGION_SOIL_OPTIONS.get(country, ["Generic Firm Sandy Gravel"])
        default_idx = 0
        prev_soil = st.session_state.selected_soil_name
        if prev_soil in soil_options:
            default_idx = soil_options.index(prev_soil)
        selected_soil = st.selectbox(
            "🌱 Soil Condition", soil_options, index=default_idx,
            format_func=lambda x: f"{x} ({get_soil_category(x)}, {get_soil_multiplier(x)}x)"
        )
        st.session_state.selected_soil_name = selected_soil

    # ─── AI weights expander ──────────────────────────────────
    with st.expander("⚖️ AI Weights", expanded=False):
        w_arch = st.slider("Architecture", 0.0, 1.0, 0.25, 0.05)
        w_struct = st.slider("Structural", 0.0, 1.0, 0.25, 0.05)
        w_sust = st.slider("Sustainability", 0.0, 1.0, 0.25, 0.05)
        w_cost = st.slider("Cost", 0.0, 1.0, 0.25, 0.05)
        total_w = w_arch + w_struct + w_sust + w_cost
        if total_w > 0:
            w_arch /= total_w
            w_struct /= total_w
            w_sust /= total_w
            w_cost /= total_w
        weights = (w_arch, w_struct, w_sust, w_cost)
        st.caption(f"Norm: arch {w_arch:.2f} struct {w_struct:.2f} sust {w_sust:.2f} cost {w_cost:.2f}")

    # ─── Generate button ──────────────────────────────────────
    if st.button("✨ Generate Concepts", use_container_width=True):
        with st.spinner("Synthesizing 5 concepts..."):
            concepts = []
            soil_name = st.session_state.selected_soil_name
            for i in range(5):
                d = generate_spatial_model(
                    domain, typology,
                    plot + random.randint(-400, 400),
                    max(1, floors + random.randint(-2, 2)),
                    max(1, baths + random.randint(-2, 2)),
                    country, soil_name, seed=i
                )
                d["plan"] = d["rooms"]  # compatibility
                ec = run_eurocode_analysis(d, domain)
                d["eurocode"] = ec
                total_usd, total_local, fx, boq_breakdown = compute_boq(d, country)
                arch, struct, sust, cost, comp = calculate_ai_scores(d, ec, total_usd, "", weights)
                materials = compute_materials(d)
                d["scores"] = {"arch": arch, "struct": struct, "sust": sust, "cost": cost, "composite": comp}
                d["total_usd"] = total_usd
                d["total_local"] = total_local
                d["fx"] = fx
                d["boq_breakdown"] = boq_breakdown
                d["materials"] = materials
                concepts.append(d)

            concepts.sort(key=lambda x: x["scores"]["composite"], reverse=True)
            st.session_state.generated_concepts = concepts
            st.session_state.active_design = concepts[0]
            log_event(username, mem, f"Generated 5 concepts. Alpha: {concepts[0]['id']}")
            leveled_up = add_xp(username, 20)
            st.session_state.user_data = get_user(username)
            if leveled_up:
                st.balloons()
            st.rerun()

    # ─── Forex converter ──────────────────────────────────────
    with st.expander("💱 Forex Converter", expanded=False):
        if st.button("🔄 Refresh Rates", use_container_width=True):
            init_fx.clear()
            init_fx()
            st.rerun()
        curr_list = ["USD"] + list(STATIC_FX.keys())
        from_cur = st.selectbox("From", curr_list, key="conv_from")
        to_cur = st.selectbox("To", curr_list, key="conv_to")
        amount = st.number_input("Amount", value=1000.0, step=100.0)
        res = convert_currency(amount, from_cur, to_cur)
        sym_from = "$" if from_cur == "USD" else get_fx(from_cur)["symbol"]
        sym_to = "$" if to_cur == "USD" else get_fx(to_cur)["symbol"]
        st.metric(f"{sym_from} {amount:,.2f}", f"{sym_to} {res:,.2f}")

    if st.button("🚪 Logout", use_container_width=True):
        save_memory(username, mem)
        st.session_state.logged_in = False
        st.rerun()

# ─── MAIN CONTENT ─────────────────────────────────────────────
if nav == "Dashboard":
    st.markdown("""
    <div class='glass-panel' style='text-align:center;margin-bottom:24px;'>
        <h2 style='margin:0;color:#aaaaaa;'>Welcome back, Architect 👋</h2>
        <p style='color:#888;'>Create. Evolve. Perfect.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 💹 Live East African FX Rates")
    cols = st.columns(6)
    for i, c in enumerate(get_all_countries()):
        data = get_fx(c)
        rate = data["rate"]
        base = _BASELINE_RATES[c]
        change = ((rate - base) / base) * 100
        color = "#888" if change >= 0 else "#555"
        with cols[i]:
            st.markdown(f"""
            <div class='glass-panel' style='padding:12px 4px;text-align:center;'>
                <div style='font-size:0.75rem;color:#888;'>{c}</div>
                <div style='font-size:1.3rem;font-weight:600;color:#ccc;'>{data['symbol']} {rate:.2f}</div>
                <div style='font-size:0.7rem;color:{color};'>{'+' if change>=0 else ''}{change:.2f}%</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    with st.expander("📈 East African FX History (60 days)", expanded=True):
        end_date = datetime.today()
        start_date = end_date - timedelta(days=60)
        df_hist = fetch_hist(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        if df_hist is not None and not df_hist.empty:
            st.plotly_chart(plot_hist(df_hist), use_container_width=True)
        else:
            st.info("Live data unavailable – showing simulated trends.")
            base_rates = {c: _CURRENT_RATES[c] for c in get_all_countries()}
            sim = {}
            dates = [start_date + timedelta(days=i) for i in range(61)]
            for c, r in base_rates.items():
                rng = np.random.default_rng(42)
                steps = rng.normal(0, 0.005, len(dates) - 1)
                vals = [r]
                for s in steps:
                    vals.append(vals[-1] * (1 + s))
                sim[c] = vals[1:]
            df_sim = pd.DataFrame(sim, index=dates[1:])
            st.plotly_chart(plot_hist(df_sim), use_container_width=True)

    st.markdown("---")
    st.markdown("### 🌳 Forex Forest – Weekly Forecast")
    st.caption("Monte Carlo simulation of possible rate paths over the next 7 days")
    fc = st.selectbox("Country", get_all_countries(), key="forest")
    fig_forest = forest(_CURRENT_RATES[fc])
    st.plotly_chart(fig_forest, use_container_width=True)

    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    c1.metric("Blueprints", len(mem["designs"]), delta="+1")
    c2.metric("Concepts", len(mem["designs"]) * 5, delta="Evolving")
    c3.metric("Logs", len(mem["logs"]))

elif nav == "Concepts":
    if st.session_state.generated_concepts:
        concepts = st.session_state.generated_concepts
        st.markdown("## 🔬 Evolution Engine Results")
        st.caption("5 unique design concepts evaluated by Sai AI Agents")
        names = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon"]
        colors = ["#888", "#999", "#777", "#666", "#555"]
        tabs = st.tabs(names[:len(concepts)])

        for idx, (tab, c) in enumerate(zip(tabs, concepts)):
            with tab:
                sc = c["scores"]
                ec = c["eurocode"]

                st.markdown(f"**Design brief:** {c['type']}, {c['floors']}‑storey, {len(c['rooms'])} rooms, {c['country']}. Soil: {c['soil_name']}. GFA: {format_area(c['total_gfa'], st.session_state.unit_system)}")

                col1, col2 = st.columns([3, 2])
                with col1:
                    st.markdown("### 🗺️ 2D Floor Plan")
                    st.plotly_chart(
                        render_floorplan(c["plan"], c["structural"]["span"]),
                        use_container_width=True,
                        key=f"fp_{c['id']}"
                    )
                    st.caption(f"Floor Area: {format_area(c['floor_area'], st.session_state.unit_system)} | {c['floors']} floors | {c['country']}")
                    with st.expander("🧱 Material Breakdown"):
                        st.dataframe(pd.DataFrame(c['boq_breakdown']), use_container_width=True)

                with col2:
                    for lbl, key, col in [
                        ("🏛️ Architect AI", "arch", "#888"),
                        ("⚙️ Structural AI", "struct", "#aaa"),
                        ("🌱 Sustainability AI", "sust", "#777"),
                        ("💰 Cost AI", "cost", "#999")
                    ]:
                        st.markdown(f"""
                        <div style='margin-bottom:6px;'>
                            <div style='display:flex;align-items:center;font-size:12px;color:#888'>{lbl} {sc[key]}%</div>
                            <div class='metric-bar-bg'><div class='metric-bar-fg' style='width:{sc[key]}%;background:{col};'></div></div>
                        </div>
                        """, unsafe_allow_html=True)
                    st.metric("USD Total", f"${c['total_usd']:,.0f}")
                    st.metric(f"Local ({c['fx']['currency']})", f"{c['fx']['symbol']} {c['total_local']:,.0f}")

                    st.markdown("### 📦 3D Massing")
                    view = st.radio("View", ["Isometric", "Interactive"], horizontal=True, key=f"view_{c['id']}")
                    if view == "Isometric":
                        st.components.v1.html(render_isometric(c["plan"], c["structural"]["span"]), height=400)
                    else:
                        st.plotly_chart(
                            render_3d(c["plan"], c["floors"], c["structural"]["span"]),
                            use_container_width=True,
                            key=f"plot_{c['id']}"
                        )

                # ─── AEC DETAILS EXPANDER ──────────────────────
                with st.expander("🧰 AEC Details (Structural, Materials, Carbon, Risks, Quality)", expanded=False):
                    st.markdown("#### 🧱 Structural Design")
                    st.write(f"**Foundation:** {c['structural']['foundation']}")
                    st.write(f"**Slab System:** {c['structural']['slab_system']}")
                    st.write(f"**Storey Height:** {format_length(c['structural']['storey_height'], st.session_state.unit_system)}")
                    st.write(f"**Wall Type:** {c['structural']['wall_type']}")
                    st.write(f"**Concrete Grade:** {c['structural']['concrete_grade']}")
                    st.write(f"**Steel Grade:** {c['structural']['steel_grade']}")
                    st.write(f"**Columns:** {c['structural']['columns']}")
                    st.write(f"**Beams:** {c['structural']['beams']}")
                    st.write(f"**Typical Span:** {format_length(c['structural']['span'], st.session_state.unit_system)}")

                    st.markdown("#### 📐 Eurocode Check")
                    st.write(f"**Design Load:** {ec['design_load']}")
                    st.write(f"**M_ed:** {ec['m_ed']}")
                    st.write(f"**M_rd:** {ec['m_rd']}")
                    st.write(f"**Status:** {ec['uls_status']}")

                    st.markdown("#### 📦 Material Quantities & Embodied Carbon")
                    mats = c['materials']
                    st.write(f"**Concrete:** {mats['concrete_volume']} m³")
                    st.write(f"**Steel:** {mats['steel_weight']} kg")
                    st.write(f"**Brick:** {mats['brick_units']} units")
                    st.write(f"**Finishes:** {format_area(mats['finish_area'], st.session_state.unit_system)}")
                    st.write(f"**Embodied Carbon:** {mats['embodied_carbon_t']} t CO₂e")

                    st.markdown("#### 💰 Detailed BOQ")
                    st.dataframe(pd.DataFrame(c['boq_breakdown']), use_container_width=True)

                    # ── Structural Member Sizing ──
                    st.markdown("#### 🏗️ Structural Member Sizing")
                    sd = compute_structural_design(c, ec)
                    col_s1, col_s2, col_s3 = st.columns(3)
                    with col_s1:
                        st.write(f"**Columns:** {format_length(sd['column_width'], st.session_state.unit_system)} × {format_length(sd['column_depth'], st.session_state.unit_system)}")
                        st.write(f"**Beams:** {format_length(sd['beam_width'], st.session_state.unit_system)} × {format_length(sd['beam_depth'], st.session_state.unit_system)}")
                    with col_s2:
                        st.write(f"**Slab:** {format_length(sd['slab_thickness'], st.session_state.unit_system)} thick")
                        st.write(f"**Footing:** {format_length(sd['footing_width'], st.session_state.unit_system)} wide")
                    with col_s3:
                        st.write(f"**Beam Rebar:** {sd['beam_bars']}×20mm bars")
                        st.write(f"**Column Rebar:** {sd['column_bars']}×25mm bars")
                        st.write(f"**Slab Rebar:** {sd['slab_bars']}×12mm @200mm")
                        st.write(f"**Footing Rebar:** {sd['footing_bars']}×16mm")

                    # ── Construction Schedule ──
                    st.markdown("#### 📅 Construction Schedule")
                    schedule_df = compute_construction_schedule(c)
                    st.dataframe(schedule_df[["Task", "Duration", "Start", "Finish", "Predecessors"]], use_container_width=True)
                    st.plotly_chart(plot_schedule_gantt(schedule_df), use_container_width=True)

                    # ── Cost by Trade ──
                    st.markdown("#### 💵 Cost by Trade")
                    cost_df = compute_cost_by_trade(c, c["country"])
                    st.dataframe(
                        cost_df.style.format({
                            "Material": "${:,.0f}",
                            "Labour": "${:,.0f}",
                            "Equipment": "${:,.0f}",
                            "Total": "${:,.0f}",
                            "Total Local": "{:,.0f}"
                        }),
                        use_container_width=True
                    )

                    # ── Solar & Energy ──
                    st.markdown("#### ☀️ Solar & Energy Analysis")
                    solar = compute_solar_potential(c)
                    col_e1, col_e2, col_e3 = st.columns(3)
                    with col_e1:
                        st.metric("Roof Area", f"{format_area(solar['roof_area'], st.session_state.unit_system)}")
                        st.metric("Installed PV", f"{solar['installed_capacity']} kWp")
                    with col_e2:
                        st.metric("Annual Energy", f"{solar['annual_energy']:,} kWh")
                        st.metric("CO₂ Savings", f"{solar['co2_savings']} tonnes/yr")
                    with col_e3:
                        st.caption("PV Performance")
                        st.progress(min(1.0, solar['annual_energy'] / 5000), text=f"{solar['annual_energy']} kWh/yr")

                    # ── Water Efficiency ──
                    st.markdown("#### 💧 Water Efficiency & Rainwater Harvesting")
                    water = compute_water_harvesting(c)
                    st.write(f"**Rainfall:** {water['rainfall']} mm/year")
                    st.write(f"**Harvestable Volume:** {water['harvestable_volume']} m³/year")
                    st.progress(water['savings_percentage'] / 100, text=f"{water['savings_percentage']}% of typical water use")
                    st.caption("Typical building water use: 100 m³/year")

                    # ── Green Rating ──
                    st.markdown("#### 🏅 Green Building Rating")
                    rating = compute_green_rating(c, ec)
                    st.metric("Score", f"{rating['score']}/100", delta=rating['rating'])
                    st.progress(rating['score'] / 100, text=f"{rating['score']}%")

                    # ── Risk Register ──
                    st.markdown("#### ⚠️ Risk Register")
                    risks = [
                        {"Risk": "Foundation settlement", "Likelihood": "Medium", "Impact": "High", "Mitigation": "Soil improvement"},
                        {"Risk": "Steel supply delay", "Likelihood": "High", "Impact": "Medium", "Mitigation": "Pre-order steel"},
                        {"Risk": "Labour shortage", "Likelihood": "Low", "Impact": "Medium", "Mitigation": "Local hiring plan"},
                        {"Risk": "Weather disruption", "Likelihood": "Medium", "Impact": "Low", "Mitigation": "Flexible schedule"},
                        {"Risk": "Cost overrun", "Likelihood": "High", "Impact": "High", "Mitigation": "10% contingency"}
                    ]
                    st.table(pd.DataFrame(risks))

                    # ── Quality Checklist ──
                    st.markdown("#### ✅ Quality Checklist")
                    checklist = [
                        {"Phase": "Foundation", "Item": "Excavation depth", "Status": "✅ Pass"},
                        {"Phase": "Foundation", "Item": "Reinforcement placement", "Status": "✅ Pass"},
                        {"Phase": "Foundation", "Item": "Concrete pour", "Status": "✅ Pass"},
                        {"Phase": "Structure", "Item": "Column alignment", "Status": "✅ Pass"},
                        {"Phase": "Structure", "Item": "Beam formwork", "Status": "✅ Pass"},
                        {"Phase": "Structure", "Item": "Slab curing", "Status": "✅ Pass"},
                        {"Phase": "Finishes", "Item": "Floor flatness", "Status": "✅ Pass"},
                        {"Phase": "Finishes", "Item": "Wall plaster", "Status": "✅ Pass"},
                        {"Phase": "Finishes", "Item": "Painting", "Status": "✅ Pass"},
                        {"Phase": "MEP", "Item": "Electrical conduit", "Status": "✅ Pass"},
                        {"Phase": "MEP", "Item": "Plumbing layout", "Status": "✅ Pass"},
                        {"Phase": "MEP", "Item": "HVAC", "Status": "✅ Pass"},
                        {"Phase": "External", "Item": "Drainage", "Status": "✅ Pass"},
                        {"Phase": "External", "Item": "Landscaping", "Status": "✅ Pass"},
                        {"Phase": "External", "Item": "Access roads", "Status": "✅ Pass"}
                    ]
                    st.table(pd.DataFrame(checklist))

        # ─── Radar across all concepts ────────────────────────
        with st.expander("📊 AI Score Radar (all concepts)", expanded=False):
            radar_df = pd.DataFrame([
                {
                    "Concept": f"{names[i]} ({c['type']})",
                    "Architecture": c["scores"]["arch"],
                    "Structural": c["scores"]["struct"],
                    "Sustainability": c["scores"]["sust"],
                    "Cost Efficiency": c["scores"]["cost"]
                }
                for i, c in enumerate(concepts)
            ])
            cats = list(radar_df.columns[1:])
            fig_radar = go.Figure()
            for i, row in radar_df.iterrows():
                fig_radar.add_trace(go.Scatterpolar(
                    r=row[cats].values,
                    theta=cats,
                    fill='toself',
                    name=row["Concept"],
                    line_color=colors[i]
                ))
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(range=[0, 100])),
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#aaaaaa'
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        # ─── Top recommendation ──────────────────────────────
        asset = concepts[0]
        st.markdown("---")
        st.markdown("### 🏆 TOP RECOMMENDATION: CONCEPT ALPHA")
        col_save, col_export = st.columns(2)
        if col_save.button("💾 Save to Library"):
            mem["designs"].append({
                "id": asset["id"],
                "type": asset["type"],
                "country": asset["country"],
                "soil": asset["soil_name"],
                "total_gfa": asset["total_gfa"],
                "scores": asset["scores"],
                "plan": asset["plan"],
                "timestamp": datetime.now().isoformat()
            })
            save_memory(username, mem)
            st.success("Design saved!")
        with col_export:
            exp = pd.DataFrame([
                {
                    "ID": c["id"],
                    "Type": c["type"],
                    "Country": c["country"],
                    "Soil": c["soil_name"],
                    "GFA": c["total_gfa"],
                    "Floors": c["floors"],
                    "Rooms": len(c["rooms"]),
                    "Cost USD": c["total_usd"],
                    "Cost Local": c["total_local"],
                    "Arch%": c["scores"]["arch"],
                    "Struct%": c["scores"]["struct"],
                    "Sust%": c["scores"]["sust"],
                    "CostEff%": c["scores"]["cost"],
                    "Composite": c["scores"]["composite"]
                }
                for c in concepts
            ])
            st.download_button(
                "📥 Export CSV",
                exp.to_csv(index=False).encode(),
                file_name="arc_concepts.csv",
                mime="text/csv"
            )
    else:
        st.info("No designs generated yet. Configure parameters in sidebar and click **Generate Concepts**.")

elif nav == "Ram AI":
    st.markdown("## 🧠 Ram AI – Infinite Architectural Intelligence")
    st.markdown("Ask Ram anything about construction, soil, costs, or design in East Africa.")
    with st.form("ram_form"):
        q = st.text_input("Your question:", placeholder="Ask Ram about soil, foundations, costs...")
        submitted = st.form_submit_button("Ask Ram AI")
    if submitted and q:
        with st.spinner("Ram is thinking..."):
            resp = ram_ai(q, country, domain)
            st.session_state.ram_history.append(("You", q))
            st.session_state.ram_history.append(("Ram", resp))
    for speaker, msg in st.session_state.ram_history:
        if speaker == "You":
            st.markdown(f"**👤 {speaker}:** {msg}")
        else:
            st.markdown(f'**🧠 {speaker}:** {msg}')

st.markdown(
    "<div style='text-align:center;padding:20px 0;color:#444'>AI Powered · Data Driven · Secure · Scalable</div>",
    unsafe_allow_html=True
)