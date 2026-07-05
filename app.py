import streamlit as st
import pandas as pd

from backend.patient_service import (
    register_patient,
    get_dashboard,
)

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="ER Surge Intelligence",
    page_icon="🏥",
    layout="wide",
)

# --------------------------------------------------
# Sidebar
# --------------------------------------------------

st.sidebar.title("🏥 ER Surge Intelligence")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Register Patient",
        "Simulation",
        "Benchmark",
    ],
)

# ==================================================
# Dashboard
# ==================================================

if page == "Dashboard":

    dashboard, recommendation = get_dashboard()

    # ----------------------------------------
    # Header
    # ----------------------------------------

    col1, col2 = st.columns([8, 2])

    with col1:
        st.title("🏥 ER Surge Intelligence")

    with col2:
        if st.button("🔄 Refresh Dashboard"):
            st.rerun()

    st.caption(
        f"Last Updated: {pd.Timestamp.now().strftime('%d %b %Y %H:%M:%S')}"
    )

    st.divider()

    # ----------------------------------------
    # KPI Cards
    # ----------------------------------------

    total_patients = dashboard["total_patients"].sum()

    avg_wait = dashboard["average_wait"].mean()

    critical = dashboard["critical_patients"].sum()

    avg_risk = recommendation["average_risk"]

    occupancy = dashboard["occupancy_percent"].mean()

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "👥 Patients",
        total_patients,
    )

    c2.metric(
        "⏳ Avg Wait",
        f"{avg_wait:.1f} min",
    )

    c3.metric(
        "🚨 Critical",
        critical,
    )

    c4.metric(
        "📈 Risk",
        recommendation["risk"],
    )

    c5.metric(
        "🛏 Occupancy",
        f"{occupancy:.1f}%",
    )

    st.divider()

    # ----------------------------------------
    # Placeholder
    # ----------------------------------------

    st.info(
        "📊 Charts will be added in Phase 3.2"
    )

    st.divider()

    st.subheader("Department Overview")

    st.dataframe(
        dashboard,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    st.subheader("Current Recommendation")

    st.metric(
        "Priority",
        recommendation["priority"],
    )

    for action in recommendation["actions"]:
        st.success(action)

# ==================================================
# Register Patient
# ==================================================

elif page == "Register Patient":

    st.title("➕ Register New Patient")

    with st.form("patient_form"):

        age = st.number_input(
            "Age",
            min_value=0,
            max_value=120,
            value=30,
        )

        gender = st.selectbox(
            "Gender",
            [
                "Male",
                "Female",
                "Other",
            ],
        )

        race = st.selectbox(
            "Race",
            [
                "White",
                "Black",
                "Asian",
                "Hispanic",
                "Other",
            ],
        )

        department = st.selectbox(
            "Department",
            [
                "General ER",
                "General Practice",
                "Orthopedics",
                "Cardiology",
                "Neurology",
                "Gastroenterology",
                "Renal",
                "Pediatrics",
            ],
        )

        arrival_mode = st.selectbox(
            "Arrival Mode",
            [
                "Walk-in",
                "Ambulance",
                "Referral",
            ],
        )

        triage_level = st.slider(
            "Triage Level",
            1,
            5,
            3,
        )

        wait_time = st.number_input(
            "Current Wait Time (minutes)",
            min_value=0,
            max_value=300,
            value=15,
        )

        is_critical = st.checkbox(
            "Critical Patient"
        )

        case_management = st.checkbox(
            "Requires Case Management"
        )

        submitted = st.form_submit_button(
            "Register Patient"
        )

    if submitted:

        patient = {

            "age": age,

            "gender": gender,

            "race": race,

            "department": department,

            "arrival_mode": arrival_mode,

            "triage_level": triage_level,

            "wait_time_min": wait_time,

            "is_critical": is_critical,

            "case_management": case_management,

        }

        result = register_patient(patient)

        st.success("Patient registered successfully!")

# ==================================================
# Simulation
# ==================================================

elif page == "Simulation":

    st.title("🎮 Simulation")

    st.info("Coming in Phase 6.")

# ==================================================
# Benchmark
# ==================================================

elif page == "Benchmark":

    st.title("⚡ GPU Benchmark")

    st.info("Coming in Phase 7.")