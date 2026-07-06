from google.cloud import bigquery
from pathlib import Path
import pandas as pd

SERVICE_ACCOUNT = Path("credentials/service_account.json")

if SERVICE_ACCOUNT.exists():

    client = bigquery.Client.from_service_account_json(
        str(SERVICE_ACCOUNT)
    )

else:

    client = bigquery.Client()

PROJECT_ID = client.project

DATASET = "hospital_er"
TABLE = "patients"

TABLE_ID = f"{PROJECT_ID}.{DATASET}.{TABLE}"


def load_patients() -> pd.DataFrame:
    """
    Load all patient records.
    """

    query = f"""
    SELECT *
    FROM `{TABLE_ID}`
    """

    return client.query(query).to_dataframe()


def append_patient(patient_df: pd.DataFrame):
    """
    Append new patient(s).
    """

    job = client.load_table_from_dataframe(
        patient_df,
        TABLE_ID
    )

    job.result()

def append_patients(patients_df: pd.DataFrame):
    """
    Append multiple patients using a single
    BigQuery load job.
    """

    if patients_df.empty:
        return

    job = client.load_table_from_dataframe(
        patients_df,
        TABLE_ID,
    )

    job.result()

def upload_benchmark_dataset(
    dataset_df: pd.DataFrame,
    table_name: str,
):
    """
    Upload (or replace) a benchmark dataset.

    Parameters
    ----------
    dataset_df : pd.DataFrame
        Benchmark dataset to upload.

    table_name : str
        BigQuery table name
        (example: benchmark_100k).
    """

    table_id = (
        f"{PROJECT_ID}.{DATASET}.{table_name}"
    )

    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",
    )

    job = client.load_table_from_dataframe(
        dataset_df,
        table_id,
        job_config=job_config,
    )

    job.result()

def run_query(sql: str) -> pd.DataFrame:
    """
    Execute any SQL query.
    """

    return client.query(sql).to_dataframe()

def restore_baseline():
    """
    Restore the live patients table from the
    immutable baseline table.
    """

    query = f"""
    DELETE FROM `{TABLE_ID}`
    WHERE TRUE;

    INSERT INTO `{TABLE_ID}`

    SELECT *

    FROM `{PROJECT_ID}.{DATASET}.patients_baseline`;
    """

    job = client.query(query)

    job.result()