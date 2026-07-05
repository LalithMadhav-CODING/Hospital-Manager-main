import random
from datetime import datetime

import pandas as pd

from cloud.bigquery import (
    append_patient,
    load_patients,
)

from backend.pipeline import run_pipeline


def _generate_patient_id(df: pd.DataFrame) -> str:
    """
    Generate the next patient ID.
    """

    if df.empty:
        return "P000001"

    numbers = (
        df["patient_id"]
        .str.replace("P", "", regex=False)
        .astype(int)
    )

    next_id = numbers.max() + 1

    return f"P{next_id:06d}"


def register_patient(patient_data: dict):
    """
    Register a new patient,
    insert into BigQuery,
    rerun the analytics pipeline.
    """

    current_df = load_patients()

    patient = patient_data.copy()

    # ----------------------------------------
    # Auto-generated fields
    # ----------------------------------------

    patient["patient_id"] = _generate_patient_id(current_df)

    patient["arrival_time"] = datetime.utcnow()

    admitted = (
        patient["triage_level"] <= 2
        or patient["is_critical"]
    )

    patient["admitted"] = admitted

    patient["current_status"] = (
        "Under Treatment"
        if admitted
        else "Waiting"
    )

    patient["bed_id"] = (
        f"{patient['department'][:3].upper()}-{random.randint(1,99):02d}"
        if admitted
        else None
    )

    patient["length_of_stay_min"] = 0

    patient["disposition"] = (
        "Admitted"
        if admitted
        else "Pending"
    )

    patient_df = pd.DataFrame([patient])

    append_patient(patient_df)

    updated_df = load_patients()

    return run_pipeline(updated_df)


def get_dashboard():
    """
    Return dashboard and recommendation.
    """

    df = load_patients()

    _, dashboard, recommendation = run_pipeline(df)

    return dashboard, recommendation


def get_patients():
    """
    Return current patient records.
    """

    return load_patients()