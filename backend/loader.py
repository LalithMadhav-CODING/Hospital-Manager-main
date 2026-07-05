import pandas as pd

from cloud.bigquery import load_patients


def load_er_data() -> pd.DataFrame:
    """
    Load the latest patient data from BigQuery
    and ensure the dataframe is ready for the
    analytics pipeline.
    """

    df = load_patients()

    # -----------------------------
    # Data Type Enforcement
    # -----------------------------

    df["arrival_time"] = pd.to_datetime(df["arrival_time"])

    df["age"] = df["age"].astype(int)

    df["wait_time_min"] = df["wait_time_min"].astype(int)

    df["triage_level"] = df["triage_level"].astype(int)

    df["admitted"] = df["admitted"].astype(bool)

    df["is_critical"] = df["is_critical"].astype(bool)

    df["case_management"] = df["case_management"].astype(bool)

    return df