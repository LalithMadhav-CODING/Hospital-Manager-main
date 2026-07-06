import streamlit as st
import pandas as pd
import plotly.express as px
from cloud.gemini import generate_operational_summary

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

    avg_risk = recommendation["overall"]["average_risk"]

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
        recommendation["overall"]["risk"],
    )

    c5.metric(
        "📊 Capacity Utilization",
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

    # ----------------------------------------
    # Department Overview
    # ----------------------------------------

    st.subheader("Department Operations Summary")

    department_table = dashboard[
        [
            "department",
            "total_patients",
            "occupancy_percent",
            "average_wait",
            "critical_patients",
            "average_risk",
        ]
    ].copy()

    department_table.columns = [
        "Department",
        "Patients",
        "Capacity Utilization (%)",
        "Average Wait (min)",
        "Critical Patients",
        "Average Risk",
    ]

    department_table = department_table.sort_values(
        by="Capacity Utilization (%)",
        ascending=False,
    )

    department_table["Capacity Utilization (%)"] = (
        department_table["Capacity Utilization (%)"]
        .round(1)
    )

    department_table["Average Wait (min)"] = (
        department_table["Average Wait (min)"]
        .round(1)
    )

    department_table["Average Risk"] = (
        department_table["Average Risk"]
        .round(2)
    )

    st.dataframe(
        department_table,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    # ----------------------------------------
    # Operational Recommendations
    # ----------------------------------------

    st.subheader("Operational Recommendations by Department")

    risk_icons = {
        "HIGH": "🔴",
        "MODERATE": "🟡",
        "LOW": "🟢",
    }

    for dept in recommendation["departments"]:

        icon = risk_icons.get(dept["risk"], "⚪")

        title = (
            f"🏥{dept['department']} • "
            f"|{icon}  {dept['risk']} • "
            f"|{dept['occupancy']:.1f}% Occupancy"
        )

        with st.expander(title):

            c1, c2 = st.columns(2)

            with c1:

                st.metric(
                    "Priority",
                    dept["priority"],
                )

                st.metric(
                    "Average Wait",
                    f"{dept['average_wait']:.1f} min",
                )

            with c2:

                st.metric(
                    "Average Risk",
                    f"{dept['average_risk']:.2f}",
                )

                st.metric(
                    "Critical Patients",
                    dept["critical_patients"],
                )

            st.markdown("#### Recommended Actions")

            for action in dept["actions"]:
                st.success(action)
            
            # ----------------------------------------
            # Gemini Explanation
            # ----------------------------------------

            st.divider()

            if st.button(
                "✨ Explain with Gemini",
                key=f"gemini_{dept['department']}",
            ):

                with st.spinner("Generating operational summary..."):

                    metrics = {
                        "department": dept["department"],
                        "patients": int(
                            dashboard.loc[
                                dashboard["department"] == dept["department"],
                                "total_patients",
                            ].iloc[0]
                        ),
                        "capacity_utilization": dept["occupancy"],
                        "average_wait": dept["average_wait"],
                        "critical_patients": dept["critical_patients"],
                        "average_risk": dept["average_risk"],
                        "risk": dept["risk"],
                        "priority": dept["priority"],
                        "actions": dept["actions"],
                    }

                    summary = generate_operational_summary(metrics)

                st.info(summary)

    st.caption(
        "Department recommendations are generated by the ER Risk Engine using real-time operational metrics."
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