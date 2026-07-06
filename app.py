import streamlit as st
import pandas as pd
import plotly.express as px
from cloud.gemini import generate_operational_summary
from backend.simulate import create_routine_patient

from backend.patient_service import (
    register_patient,
    get_dashboard,
)
from cloud.bigquery import restore_baseline

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="ER Surge Intelligence",
    page_icon="🏥",
    layout="wide",
)

# --------------------------------------------------
# Session State Initialization
# --------------------------------------------------

if "operations_feed" not in st.session_state:
    st.session_state["operations_feed"] = []

# --------------------------------------------------
# Sidebar
# --------------------------------------------------

st.sidebar.title("🏥 ER Surge Intelligence")

PAGES = [
    "Dashboard",
    "Register Patient",
    "Simulation",
    "Benchmark",
]

if "page" not in st.session_state:
    st.session_state["page"] = "Dashboard"

page = st.sidebar.radio(
    "Navigation",
    PAGES,
    index=PAGES.index(st.session_state["page"]),
)

st.session_state["page"] = page

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

    # ----------------------------------------
    # Operational Impact Feed
    # ----------------------------------------

    if st.session_state["operations_feed"]:

        st.subheader("📡 Operational Impact Feed")

        for event in st.session_state["operations_feed"]:

            with st.expander(
                f"{event['icon']} {event['title']} • {event['time']} • {event['summary']}"
            ):

                for label, value in event["details"]:

                    left, right = st.columns([2, 3])

                    with left:
                        st.markdown(f"**{label}**")

                    with right:
                        st.write(value)

        st.divider()

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

    st.title("🎮 ER Operations Simulation")

    st.markdown(
        """
Use the controls below to simulate operational events in the Emergency Department.

Each event will eventually generate new patient arrivals, update BigQuery,
rerun the analytics pipeline, and refresh the dashboard.
"""
    )

    st.divider()

    st.subheader("Operational Scenarios")

    col1, col2 = st.columns(2)

    with col1:

        add_one = st.button(
            "🟢 Routine Arrival",
            use_container_width=True,
        )
        st.caption("Routine walk-in patient")

        ambulance = st.button(
            "🔴 Critical Ambulance Arrival",
            use_container_width=True,
        )
        st.caption("High-acuity emergency")

        reset = st.button(
            "🔄 Reset Hospital State",
            use_container_width=True,
            type="secondary",
        )
        st.caption("Restore baseline hospital")

    with col2:

        add_five = st.button(
            "🟡 Patient Surge",
            use_container_width=True,
        )
        st.caption("5 new arrivals")

        mass_casualty = st.button(
            "🚨 Mass Casualty Incident",
            use_container_width=True,
            type="primary",
        )
        st.caption("Large emergency event")

    st.divider()

    st.subheader("Scenario Status")

    if add_one:

        with st.spinner("Simulating Routine Arrival..."):

            patient = create_routine_patient()

            register_patient(patient)

            from datetime import datetime

            timestamp = datetime.now().strftime("%H:%M:%S")

            dashboard_after, recommendation_after = get_dashboard()

            capacity = dashboard_after["occupancy_percent"].mean()

            risk = recommendation_after["overall"]["risk"]

            st.session_state["scenario_result"] = {
                "title": "🟢 Routine Arrival Completed",
                "subtitle": (
                    "1 routine patient was registered successfully. "
                    "The operational analytics pipeline has completed."
                ),
                "steps": [
                    {
                        "icon": "✅",
                        "title": "Patient Generated",
                        "description": "Routine walk-in patient created successfully.",
                        "time": timestamp,
                    },
                    {
                        "icon": "☁️",
                        "title": "BigQuery Updated",
                        "description": "Patient record inserted into Google BigQuery.",
                        "time": timestamp,
                    },
                    {
                        "icon": "📊",
                        "title": "Analytics Pipeline Executed",
                        "description": "Operational metrics and dashboard data refreshed.",
                        "time": timestamp,
                    },
                    {
                        "icon": "⚠️",
                        "title": "Risk Engine Updated",
                        "description": "Department risk scores recalculated.",
                        "time": timestamp,
                    },
                    {
                        "icon": "📋",
                        "title": "Recommendations Generated",
                        "description": "Department recommendations updated.",
                        "time": timestamp,
                    },
                    {
                        "icon": "✨",
                        "title": "Gemini Ready",
                        "description": "AI operational explanations are available.",
                        "time": timestamp,
                    },
                ],
            }

            st.session_state["operations_feed"].insert(
                0,
                {
                    "icon": "🟢",
                    "title": "Routine Arrival",
                    "time": timestamp,
                    "summary": "+1 Patient Registered • Routine Walk-in",
                    "details": [
                        ("Department", patient["department"]),
                        ("Arrival Mode", patient["arrival_mode"]),
                        ("Overall Risk", risk),
                        ("Capacity Utilization", f"{capacity:.1f}%"),
                    ],
                },
            )

            st.session_state["operations_feed"] = (
                st.session_state["operations_feed"][:10]
            )

        st.rerun()

    elif add_five:

        with st.spinner("Simulating Patient Surge..."):

            from datetime import datetime

            timestamp = datetime.now().strftime("%H:%M:%S")

            progress = st.progress(0)

            for i in range(5):

                patient = create_routine_patient()

                register_patient(patient)

                progress.progress((i + 1) / 5)
            
            dashboard_after, recommendation_after = get_dashboard()
            capacity = dashboard_after["occupancy_percent"].mean()
            risk = recommendation_after["overall"]["risk"]

            st.session_state["scenario_result"] = {
                "title": "🟡 Patient Surge Completed",
                "subtitle": (
                    "5 patients were successfully registered. "
                    "The operational analytics pipeline has completed."
                ),
                "steps": [
                    {
                        "icon": "👥",
                        "title": "5 Patients Generated",
                        "description": "Five routine patient arrivals simulated.",
                        "time": timestamp,
                    },
                    {
                        "icon": "☁️",
                        "title": "BigQuery Updated",
                        "description": "All patient records inserted successfully.",
                        "time": timestamp,
                    },
                    {
                        "icon": "📊",
                        "title": "Analytics Pipeline Executed",
                        "description": "Operational metrics refreshed.",
                        "time": timestamp,
                    },
                    {
                        "icon": "⚠️",
                        "title": "Risk Engine Updated",
                        "description": "Department risk scores recalculated.",
                        "time": timestamp,
                    },
                    {
                        "icon": "📋",
                        "title": "Recommendations Generated",
                        "description": "Operational recommendations updated.",
                        "time": timestamp,
                    },
                    {
                        "icon": "✨",
                        "title": "Gemini Ready",
                        "description": "AI operational explanation available.",
                        "time": timestamp,
                    },
                ],
            }

            st.session_state["operations_feed"].insert(
                0,
                {
                    "icon": "🟡",
                    "title": "Patient Surge",
                    "time": timestamp,
                    "summary": "+5 Patients • Capacity Increased",
                    "details": [
                        ("Patients Added", "5"),
                        ("Scenario", "Routine Patient Surge"),
                        ("Overall Risk", risk),
                        ("Capacity Utilization", f"{capacity:.1f}%"),
                    ],
                },
            )

            st.session_state["operations_feed"] = (
                st.session_state["operations_feed"][:10]
            )

        st.rerun()

    elif ambulance:

        with st.spinner("Simulating Critical Ambulance Arrival..."):

            from datetime import datetime
            import random

            timestamp = datetime.now().strftime("%H:%M:%S")

            patient = create_routine_patient()

            # ----------------------------------------
            # Convert into a Critical Ambulance Arrival
            # ----------------------------------------

            patient["arrival_mode"] = "Ambulance"
            patient["triage_level"] = 1
            patient["is_critical"] = True
            patient["wait_time_min"] = random.randint(0, 5)

            # Higher probability of high-pressure departments
            patient["department"] = random.choice(
                [
                    "General ER",
                    "General ER",
                    "General ER",
                    "Cardiology",
                    "Neurology",
                ]
            )

            register_patient(patient)

            st.session_state["scenario_result"] = {
                "title": "🔴 Critical Ambulance Arrival Completed",
                "subtitle": (
                    "A high-acuity ambulance patient was successfully registered. "
                    "The operational analytics pipeline has completed."
                ),
                "steps": [
                    {
                        "icon": "🚑",
                        "title": "Critical Patient Generated",
                        "description": "Emergency ambulance arrival created.",
                        "time": timestamp,
                    },
                    {
                        "icon": "☁️",
                        "title": "BigQuery Updated",
                        "description": "Patient record inserted successfully.",
                        "time": timestamp,
                    },
                    {
                        "icon": "📊",
                        "title": "Analytics Pipeline Executed",
                        "description": "Operational metrics refreshed.",
                        "time": timestamp,
                    },
                    {
                        "icon": "⚠️",
                        "title": "Risk Engine Updated",
                        "description": "Department risk scores recalculated.",
                        "time": timestamp,
                    },
                    {
                        "icon": "📋",
                        "title": "Recommendations Generated",
                        "description": "Operational recommendations updated.",
                        "time": timestamp,
                    },
                    {
                        "icon": "✨",
                        "title": "Gemini Ready",
                        "description": "AI operational explanation available.",
                        "time": timestamp,
                    },
                ],
            }

            dashboard_after, recommendation_after = get_dashboard()
            capacity = dashboard_after["occupancy_percent"].mean()
            risk = recommendation_after["overall"]["risk"]

            st.session_state["operations_feed"].insert(
                0,
                {
                    "icon": "🔴",
                    "title": "Critical Ambulance Arrival",
                    "time": timestamp,
                    "summary": "Critical Patient • High Priority",
                    "details": [
                        ("Department", patient["department"]),
                        ("Arrival Mode", "Ambulance"),
                        ("Critical Patient", "Yes"),
                        ("Overall Risk", risk),
                        ("Capacity Utilization", f"{capacity:.1f}%"),
                    ],
                },
            )

            st.session_state["operations_feed"] = (
                st.session_state["operations_feed"][:10]
            )

        st.rerun()

    elif mass_casualty:

        with st.spinner("Simulating Mass Casualty Incident..."):

            from datetime import datetime
            import random

            timestamp = datetime.now().strftime("%H:%M:%S")

            progress = st.progress(0)

            for i in range(30):

                patient = create_routine_patient()

                # -----------------------------
                # Emergency Scenario Overrides
                # -----------------------------

                patient["arrival_mode"] = random.choices(
                    ["Ambulance", "Walk-in"],
                    weights=[70, 30],
                )[0]

                patient["triage_level"] = random.choices(
                    [1, 2, 3],
                    weights=[40, 40, 20],
                )[0]

                patient["is_critical"] = random.random() < 0.40

                patient["wait_time_min"] = random.randint(0, 15)

                patient["department"] = random.choice(
                    [
                        "General ER",
                        "General ER",
                        "General ER",
                        "Orthopedics",
                        "Neurology",
                        "Cardiology",
                    ]
                )

                register_patient(patient)

                progress.progress((i + 1) / 30)

            st.session_state["scenario_result"] = {
                "title": "🚨 Mass Casualty Incident Completed",
                "subtitle": (
                    "30 emergency patients were successfully registered. "
                    "Operational analytics have been refreshed."
                ),
                "steps": [
                    {
                        "icon": "🚨",
                        "title": "30 Emergency Patients Generated",
                        "description": "Mass casualty scenario simulated.",
                        "time": timestamp,
                    },
                    {
                        "icon": "☁️",
                        "title": "BigQuery Updated",
                        "description": "All patient records inserted successfully.",
                        "time": timestamp,
                    },
                    {
                        "icon": "📊",
                        "title": "Analytics Pipeline Executed",
                        "description": "Operational metrics refreshed.",
                        "time": timestamp,
                    },
                    {
                        "icon": "⚠️",
                        "title": "Risk Engine Updated",
                        "description": "Department risks recalculated.",
                        "time": timestamp,
                    },
                    {
                        "icon": "📋",
                        "title": "Recommendations Generated",
                        "description": "Department recommendations updated.",
                        "time": timestamp,
                    },
                    {
                        "icon": "✨",
                        "title": "Gemini Ready",
                        "description": "AI operational explanation available.",
                        "time": timestamp,
                    },
                ],
            }

            dashboard_after, recommendation_after = get_dashboard()
            capacity = dashboard_after["occupancy_percent"].mean()
            risk = recommendation_after["overall"]["risk"]

            st.session_state["operations_feed"].insert(
                0,
                {
                    "icon": "🚨",
                    "title": "Mass Casualty Incident",
                    "time": timestamp,
                    "summary": "+30 Patients • Hospital Under Stress",
                    "details": [
                        ("Patients Added", "30"),
                        ("Scenario", "Mass Casualty"),
                        ("Overall Risk", risk),
                        ("Capacity Utilization", f"{capacity:.1f}%"),
                    ],
                },
            )

            st.session_state["operations_feed"] = (
                st.session_state["operations_feed"][:10]
            )

        st.rerun()

    elif reset:

        with st.spinner("Restoring hospital state..."):

            restore_baseline()

            from datetime import datetime

            timestamp = datetime.now().strftime("%H:%M:%S")

            st.session_state["scenario_result"] = {

                "title": "🔄 Hospital State Restored",

                "subtitle": (
                    "The live hospital data has been restored "
                    "from the baseline BigQuery snapshot."
                ),

                "steps": [

                    {
                        "icon": "🗑️",
                        "title": "Live Table Cleared",
                        "description": "Current simulation data removed.",
                        "time": timestamp,
                    },

                    {
                        "icon": "☁️",
                        "title": "Baseline Restored",
                        "description": "Baseline patient records copied into the live table.",
                        "time": timestamp,
                    },

                    {
                        "icon": "📊",
                        "title": "Dashboard Ready",
                        "description": "Operational dashboard restored.",
                        "time": timestamp,
                    },

                ],
            }

            st.session_state["operations_feed"].insert(
                0,
                {
                    "icon": "🔄",
                    "title": "Hospital Reset",
                    "time": timestamp,
                    "summary": "Baseline Restored",
                    "details": [
                        (
                            "Source",
                            "BigQuery Baseline Snapshot",
                        ),
                        (
                            "Status",
                            "Hospital Restored",
                        ),
                    ],
                },
            )

            st.session_state["operations_feed"] = (
                st.session_state["operations_feed"][:10]
            )

        st.rerun()

    if "scenario_result" in st.session_state:

        result = st.session_state["scenario_result"]

        st.divider()

        st.success(result["title"])

        st.caption(result["subtitle"])

        st.markdown("### Execution Summary")

        for step in result["steps"]:

            with st.container(border=True):

                left, right = st.columns([7, 2])

                with left:

                    st.markdown(
                        f"### {step['icon']} {step['title']}"
                    )

                    st.caption(step["description"])

                with right:

                    st.markdown(
                        f"<div style='text-align:right; color:gray;'>"
                        f"🕒 {step['time']}"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

        st.divider()

        if st.button(
            "📊 View Updated Dashboard",
            use_container_width=True,
        ):

            st.session_state["page"] = "Dashboard"

            del st.session_state["scenario_result"]

            st.rerun()

# ==================================================
# Benchmark
# ==================================================

elif page == "Benchmark":

    st.title("⚡ GPU Benchmark")

    st.info("Coming in Phase 7.")