import pandas as pd

from backend.config import (
    HIGH_RISK,
    MODERATE_RISK,
)


def generate_recommendations(dashboard: pd.DataFrame) -> dict:
    """
    Generate operational recommendations based on
    department dashboard metrics.
    """

    avg_risk = dashboard["average_risk"].mean()
    avg_wait = dashboard["average_wait"].mean()
    occupancy = dashboard["occupancy_percent"].mean()

    actions = []

    # ----------------------------
    # Risk Assessment
    # ----------------------------

    if avg_risk >= HIGH_RISK:
        risk = "HIGH"
        priority = "Immediate"

        actions.extend([
            "Open overflow beds",
            "Deploy additional nursing staff",
            "Prioritize high-acuity patients"
        ])

    elif avg_risk >= MODERATE_RISK:
        risk = "MODERATE"
        priority = "Monitor"

        actions.extend([
            "Monitor patient flow",
            "Prepare additional beds if required"
        ])

    else:
        risk = "LOW"
        priority = "Routine"

        actions.append(
            "Operations within normal limits"
        )

    # ----------------------------
    # Wait Time
    # ----------------------------

    if avg_wait > 45:
        actions.append(
            "Investigate excessive patient waiting time"
        )

    # ----------------------------
    # Occupancy
    # ----------------------------

    if occupancy > 90:
        actions.append(
            "Department occupancy exceeds 90%"
        )

    return {
        "risk": risk,
        "priority": priority,
        "average_risk": round(avg_risk, 3),
        "average_wait": round(avg_wait, 1),
        "occupancy": round(occupancy, 1),
        "actions": actions,
    }