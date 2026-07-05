import pandas as pd

from backend.config import (
    RISK_WEIGHTS,
    HIGH_RISK,
    MODERATE_RISK,
)

from backend.utils import normalize


# --------------------------------------------------
# Individual Risk Components
# --------------------------------------------------

def calculate_wait_risk(df: pd.DataFrame) -> pd.DataFrame:
    """
    Risk contributed by patient waiting time.
    """

    df = df.copy()

    df["risk_wait"] = normalize(df["rolling_wait_avg"])

    return df


def calculate_load_risk(df: pd.DataFrame) -> pd.DataFrame:
    """
    Risk contributed by department workload.
    """

    df = df.copy()

    df["risk_load"] = normalize(df["relative_load"])

    return df


def calculate_acuity_risk(df: pd.DataFrame) -> pd.DataFrame:
    """
    Risk contributed by patient acuity.
    Lower triage level = higher risk.
    """

    df = df.copy()

    df["risk_acuity"] = normalize(6 - df["triage_level"])

    return df


def calculate_complexity_risk(df: pd.DataFrame) -> pd.DataFrame:
    """
    Risk contributed by operational complexity.
    """

    df = df.copy()

    complexity = (
        df["is_critical"].astype(int)
        + df["case_management"].astype(int)
        + df["admitted"].astype(int)
    )

    df["risk_complexity"] = normalize(complexity)

    return df


# --------------------------------------------------
# Composite Risk Score
# --------------------------------------------------

def calculate_total_risk(df: pd.DataFrame) -> pd.DataFrame:
    """
    Weighted operational risk score.
    """

    weights = RISK_WEIGHTS

    df["bed_risk_score"] = (

        weights["wait"] * df["risk_wait"]

        + weights["load"] * df["risk_load"]

        + weights["acuity"] * df["risk_acuity"]

        + weights["complexity"] * df["risk_complexity"]

    )

    return df


# --------------------------------------------------
# Risk Tier
# --------------------------------------------------

def assign_risk_tier(df: pd.DataFrame) -> pd.DataFrame:
    """
    Categorize patients into operational risk tiers.
    """

    df = df.copy()

    def classify(score):

        if score >= HIGH_RISK:
            return "HIGH"

        if score >= MODERATE_RISK:
            return "MODERATE"

        return "LOW"

    df["risk_tier"] = df["bed_risk_score"].apply(classify)

    return df


# --------------------------------------------------
# Risk Pipeline
# --------------------------------------------------

def calculate_risk(df: pd.DataFrame) -> pd.DataFrame:
    """
    Complete risk scoring pipeline.
    """

    df = calculate_wait_risk(df)

    df = calculate_load_risk(df)

    df = calculate_acuity_risk(df)

    df = calculate_complexity_risk(df)

    df = calculate_total_risk(df)

    df = assign_risk_tier(df)

    return df