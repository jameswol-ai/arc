import streamlit as st
        "seismic": seismic,
        "beam": beam,
        "column": column,
        "compliance": compliance,
        "ratio": ratio,
        "energy": energy,
        "carbon": carbon,
        "daylight": daylight,
        "ventilation": ventilation,
        "thought": thought,
        "evolution": evolution,
        "floorplan": floorplan,
        "time": str(datetime.now())
    }

    st.session_state.history.append(evolution)
    st.session_state.city_memory.append(result)

    return result

# =========================================================
# AUTONOMOUS LOOP
# =========================================================

if autonomous:
    st.session_state.autonomous_mode = True
else:
    st.session_state.autonomous_mode = False

if run_cycle:
    latest = run_simulation_cycle()

if st.session_state.autonomous_mode:

    auto_placeholder = st.empty()

    for _ in range(2):
        latest = run_simulation_cycle()

        auto_placeholder.success(
            f"Autonomous Cycle {latest['cycle']} completed"
        )

        time.sleep(1)

# =========================================================
# DISPLAY LATEST RESULT
# =========================================================

if len(st.session_state.city_memory) > 0:

    latest = st.session_state.city_memory[-1]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Evolution", latest["evolution"])

    with col2:
        st.metric("Energy Score", latest["energy"])

    with col3:
        st.metric("Carbon", latest["carbon"])

    with col4:
        st.metric("Utilization", latest["ratio"])

    st.markdown("---")

    # =====================================================
    # AI THOUGHTS
    # =====================================================

    st.subheader("🧠 RANDOM 
