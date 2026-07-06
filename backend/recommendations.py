import pandas as pd

from backend.config import (
    HIGH_RISK,
    MODERATE_RISK,
)


def _build_recommendation(avg_risk, avg_wait, occupancy):
    """
    Build a recommendation from operational metrics.
    """

    actions = []

    if avg_risk >= HIGH_RISK:
        risk = "HIGH"
        priority = "Immediate"

        actions.extend([
            "Open overflow beds",
            "Deploy additional nursing staff",
            "Prioritize high-acuity patients",
        ])

    elif avg_risk >= MODERATE_RISK:
        risk = "MODERATE"
        priority = "Monitor"

        actions.extend([
            "Monitor patient flow",
            "Prepare additional beds if required",
        ])

    else:
        risk = "LOW"
        priority = "Routine"

        actions.append(
            "Operations within normal limits. Continue routine monitoring and maintain current staffing levels."
        )

    if avg_wait > 45:
        actions.append(
            "Review patient flow to reduce prolonged waiting times."
        )

    if occupancy > 90:
        actions.append(
            "Department occupancy exceeds 90%. Prepare overflow capacity and consider staff reallocation."
        )

    return {
        "risk": risk,
        "priority": priority,
        "average_risk": round(avg_risk, 3),
        "average_wait": round(avg_wait, 1),
        "occupancy": round(occupancy, 1),
        "actions": actions,
    }

def generate_recommendations(dashboard: pd.DataFrame) -> dict:
    """
    Generate hospital-wide and department-level recommendations.
    """

    overall = _build_recommendation(
        dashboard["average_risk"].mean(),
        dashboard["average_wait"].mean(),
        dashboard["occupancy_percent"].mean(),
    )

    departments = []

    for _, row in dashboard.iterrows():

        department = _build_recommendation(
            row["average_risk"],
            row["average_wait"],
            row["occupancy_percent"],
        )

        department["department"] = row["department"]
        department["critical_patients"] = int(row["critical_patients"])

        departments.append(department)

    priority_order = {
        "HIGH": 0,
        "MODERATE": 1,
        "LOW": 2,
    }

    departments.sort(
        key=lambda x: (
            priority_order[x["risk"]],
            -x["occupancy"],
            -x["average_wait"],
        )
    )

    return {
        "overall": overall,
        "departments": departments,
    }