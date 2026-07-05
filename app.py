import streamlit as st
import pandas as pd
import plotly.express as px

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
    # Charts
    # ----------------------------------------

    chart_data = dashboard.sort_values("occupancy_percent", ascending=False)

    left, right = st.columns(2)

    with left:

        fig = px.bar(
            chart_data,
            x="department",
            y="occupancy_percent",
            color="occupancy_percent",
            title="Department Capacity Utilization",
            labels={
                "department": "Department",
                "occupancy_percent": "Occupancy (%)",
            },
            text_auto=".1f",
        )

        fig.update_layout(
            template="plotly_white",
            height=400,
            coloraxis_showscale=False,
            margin=dict(l=20, r=20, t=50, b=20),
        )

        fig.update_traces(
            hovertemplate="<b>%{x}</b><br>Occupancy: %{y:.1f}%<extra></extra>"
        )

        st.plotly_chart(fig, use_container_width=True)

    with right:

        fig = px.bar(
            dashboard.sort_values("average_wait", ascending=False),
            x="department",
            y="average_wait",
            color="average_wait",
            title="Average Wait Time",
            labels={
                "department": "Department",
                "average_wait": "Minutes",
            },
            text_auto=".1f",
        )

        fig.update_layout(
            template="plotly_white",
            height=400,
            coloraxis_showscale=False,
            margin=dict(l=20, r=20, t=50, b=20),
        )

        fig.update_traces(
            hovertemplate="<b>%{x}</b><br>Wait: %{y:.1f} min<extra></extra>"
        )

        st.plotly_chart(fig, use_container_width=True)

    left, right = st.columns(2)

    with left:

        fig = px.bar(
            dashboard.sort_values("critical_patients", ascending=False),
            x="department",
            y="critical_patients",
            color="critical_patients",
            title="Critical Patients by Department",
            labels={
                "department": "Department",
                "critical_patients": "Patients",
            },
            text_auto=True,
        )

        fig.update_layout(
            template="plotly_white",
            height=400,
            coloraxis_showscale=False,
            margin=dict(l=20, r=20, t=50, b=20),
        )

        fig.update_traces(
            hovertemplate="<b>%{x}</b><br>Critical: %{y}<extra></extra>"
        )

        st.plotly_chart(fig, use_container_width=True)

    with right:

        fig = px.bar(
            dashboard.sort_values("average_risk", ascending=False),
            x="department",
            y="average_risk",
            color="average_risk",
            title="Average Risk Score",
            labels={
                "department": "Department",
                "average_risk": "Risk Score",
            },
            text_auto=".2f",
        )

        fig.update_layout(
            template="plotly_white",
            height=400,
            coloraxis_showscale=False,
            margin=dict(l=20, r=20, t=50, b=20),
        )

        fig.update_traces(
            hovertemplate="<b>%{x}</b><br>Risk: %{y:.2f}<extra></extra>"
        )

        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("Department Overview")

    st.dataframe(
        dashboard,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    # ----------------------------------------
    # Operational Recommendation
    # ----------------------------------------

    st.subheader("Operational Recommendation")

    risk = recommendation["risk"]

    if risk == "HIGH":
        risk_badge = "🔴 HIGH"
    elif risk == "MEDIUM":
        risk_badge = "🟡 MEDIUM"
    else:
        risk_badge = "🟢 LOW"

    left, right = st.columns([1, 2])

    with left:

        st.metric(
            "Current Risk",
            risk_badge,
        )

        st.metric(
            "Priority",
            recommendation["priority"],
        )

        st.metric(
            "Average Wait",
            f"{recommendation['average_wait']:.1f} min",
        )

        st.metric(
            "Occupancy",
            f"{recommendation['occupancy']:.1f}%",
        )

    with right:

        st.markdown("### Recommended Actions")

        for action in recommendation["actions"]:
            st.success(action)

    st.caption(
        "Recommendations are generated from the ER risk engine using current operational metrics."
    )
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