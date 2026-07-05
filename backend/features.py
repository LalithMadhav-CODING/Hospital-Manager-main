import pandas as pd

from backend.config import DEPARTMENT_BED_CAPACITY


# --------------------------------------------------
# Time Features
# --------------------------------------------------

def create_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create time-based operational features.
    """

    df = df.copy()

    df["arrival_hour"] = df["arrival_time"].dt.hour
    df["arrival_day"] = df["arrival_time"].dt.day_name()
    df["arrival_month"] = df["arrival_time"].dt.month

    return df


# --------------------------------------------------
# Department Features
# --------------------------------------------------

def create_department_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute department workload statistics.
    """

    df = df.copy()

    department_load = (
        df.groupby("department")
        .size()
        .rename("department_load")
    )

    df = df.merge(
        department_load,
        on="department",
        how="left"
    )

    df["department_capacity"] = (
        df["department"]
        .map(DEPARTMENT_BED_CAPACITY)
        .fillna(20)
    )

    df["relative_load"] = (
        df["department_load"]
        / df["department_capacity"]
    )

    return df


# --------------------------------------------------
# Wait Features
# --------------------------------------------------

def create_wait_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rolling wait-time statistics.
    """

    df = df.copy()

    df = df.sort_values("arrival_time")

    df["rolling_wait_avg"] = (
        df["wait_time_min"]
        .rolling(window=10, min_periods=1)
        .mean()
    )

    return df


# --------------------------------------------------
# Admission Features
# --------------------------------------------------

def create_admission_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rolling admission rate.
    """

    df = df.copy()

    df["rolling_admission_rate"] = (
        df["admitted"]
        .astype(int)
        .rolling(window=10, min_periods=1)
        .mean()
    )

    return df


# --------------------------------------------------
# Critical Case Features
# --------------------------------------------------

def create_critical_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rolling critical patient rate.
    """

    df = df.copy()

    df["rolling_critical_rate"] = (
        df["is_critical"]
        .astype(int)
        .rolling(window=10, min_periods=1)
        .mean()
    )

    return df


# --------------------------------------------------
# Feature Engineering Pipeline
# --------------------------------------------------

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Complete feature engineering pipeline.
    """

    df = create_time_features(df)

    df = create_department_features(df)

    df = create_wait_features(df)

    df = create_admission_features(df)

    df = create_critical_features(df)

    return df