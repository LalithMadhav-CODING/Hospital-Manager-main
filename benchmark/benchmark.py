import time

import pandas as pd

from cloud.bigquery import run_query


# =====================================================
# Benchmark Dataset Loader
# =====================================================

DATASET_TABLES = {
    "10K": "benchmark_patients_10000",
    "20K": "benchmark_patients_20000",
    "50K": "benchmark_patients_50000",
    "100K": "benchmark_patients_100000",
    "250K": "benchmark_patients_250000",
    "500K": "benchmark_patients_500000",
    "1M": "benchmark_patients_1000000",
}


def load_benchmark_dataset(dataset_size: str) -> pd.DataFrame:
    """
    Load a benchmark dataset from BigQuery.

    Benchmark timing DOES NOT include
    dataset loading.
    """

    table = DATASET_TABLES[dataset_size]

    query = f"""
    SELECT *
    FROM hospital_er.{table}
    """

    return run_query(query)


# =====================================================
# Benchmark Timer
# =====================================================

def measure_execution(func, *args, **kwargs):
    """
    Measure execution time of a workload.

    Dataset loading is expected to happen
    before calling this function.
    """

    start = time.perf_counter()

    result = func(*args, **kwargs)

    end = time.perf_counter()

    elapsed = end - start

    return result, elapsed


# =====================================================
# Benchmark Result
# =====================================================

def build_result(
    workload_name: str,
    dataset_size: str,
    rows: int,
    cpu_time: float,
    gpu_time=None,
):
    """
    Standard benchmark result object.
    """

    rows_per_second = rows / cpu_time if cpu_time > 0 else 0

    speedup = None

    if gpu_time not in (None, 0):
        speedup = cpu_time / gpu_time

    return {
        "workload": workload_name,
        "dataset": dataset_size,
        "rows": rows,
        "cpu_time": cpu_time,
        "gpu_time": gpu_time,
        "speedup": speedup,
        "rows_per_second": rows_per_second,
    }

# =====================================================
# Workload 1 - Patient Lookup
# =====================================================

def patient_lookup(df):
    """
    Benchmark workload:
    Lookup a patient by ID.
    """

    patient_id = df.iloc[len(df) // 2]["patient_id"]

    return df[df["patient_id"] == patient_id]


def run_patient_lookup_cpu(dataset_size: str):
    """
    Execute the Patient Lookup benchmark using Pandas.
    """

    df = load_benchmark_dataset(dataset_size)

    _, cpu_time = measure_execution(
        patient_lookup,
        df,
    )

    return build_result(
        workload_name="Patient Lookup",
        dataset_size=dataset_size,
        rows=len(df),
        cpu_time=cpu_time,
    )

