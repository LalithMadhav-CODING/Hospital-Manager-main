import pandas as pd


# --------------------------------------------------
# Dashboard Builder
# --------------------------------------------------

def build_dashboard(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build department-level operational dashboard.
    """

    dashboard = (
        df.groupby("department")
        .agg(
            total_patients=("patient_id", "count"),

            average_wait=("wait_time_min", "mean"),

            average_risk=("bed_risk_score", "mean"),

            average_load=("relative_load", "mean"),

            critical_patients=("is_critical", "sum"),

            admitted_patients=("admitted", "sum"),

            case_management_patients=("case_management", "sum"),

            average_triage=("triage_level", "mean"),
        )
        .reset_index()
    )

    dashboard["occupancy_percent"] = (
        dashboard["average_load"] * 100
    ).round(1)

    dashboard["average_wait"] = (
        dashboard["average_wait"]
    ).round(1)

    dashboard["average_risk"] = (
        dashboard["average_risk"]
    ).round(3)

    dashboard["average_triage"] = (
        dashboard["average_triage"]
    ).round(2)

    return dashboard