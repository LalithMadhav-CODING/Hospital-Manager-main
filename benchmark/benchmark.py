import time

import pandas as pd

from cloud.bigquery import run_query

from backend.features import engineer_features

from backend.risk import calculate_risk

from backend.recommendations import generate_recommendations

from backend.pipeline import run_pipeline

try:

    import cudf

    GPU_AVAILABLE = True

except ImportError:

    GPU_AVAILABLE = False

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


import streamlit as st


@st.cache_data(show_spinner=False)
def load_benchmark_dataset(dataset_size: str) -> pd.DataFrame:
    """
    Load a benchmark dataset from BigQuery.

    The dataset is cached so that benchmark timings
    measure only the workload execution and not
    repeated BigQuery downloads.
    """

    table = DATASET_TABLES[dataset_size]

    query = f"""
    SELECT *
    FROM hospital_er.{table}
    """

    return run_query(query)

def load_gpu_benchmark_dataset(dataset_size):
    """
    Load benchmark dataset as a cuDF DataFrame.
    """

    if not GPU_AVAILABLE:
        raise RuntimeError(
            "GPU environment not available."
        )

    pdf = load_benchmark_dataset(dataset_size)

    return cudf.DataFrame.from_pandas(pdf)

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

def run_gpu_workload(
    dataset_size,
    workload,
    workload_name,
):

    gdf = load_gpu_benchmark_dataset(
        dataset_size
    )

    _, gpu_time = measure_execution(
        workload,
        gdf,
    )

    return gpu_time

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

    }

# =====================================================
# Workload 1 - Patient Lookup
# =====================================================

def patient_lookup(df):
    """
    Benchmark workload:
    Lookup a patient by ID.
    """

    patient_id = df["patient_id"].sample(
        n=1,
        random_state=None,
    ).iloc[0]

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

# =====================================================
# Workload 2 - Department Patient Lookup
# =====================================================

def department_patient_lookup(df):
    """
    Benchmark workload:
    Retrieve all patients from General ER.
    """

    department = (
        df["department"]
        .sample(n=1)
        .iloc[0]
    )

    return df[
        df["department"] == department
    ]


def run_department_lookup_cpu(dataset_size: str):

    df = load_benchmark_dataset(dataset_size)

    _, cpu_time = measure_execution(
        department_patient_lookup,
        df,
    )

    return build_result(
        workload_name="Department Patient Lookup",
        dataset_size=dataset_size,
        rows=len(df),
        cpu_time=cpu_time,
    )

# =====================================================
# Workload 3 - Critical Patient Queue
# =====================================================

def critical_patient_queue(df):
    """
    Return critical patients ordered by
    triage level and wait time.
    """

    queue = df[
        df["is_critical"] == True
    ]

    queue = queue.sort_values(
        by=[
            "triage_level",
            "wait_time_min",
        ]
    )

    return queue


def run_critical_queue_cpu(dataset_size: str):

    df = load_benchmark_dataset(dataset_size)

    _, cpu_time = measure_execution(
        critical_patient_queue,
        df,
    )

    return build_result(
        workload_name="Critical Patient Queue",
        dataset_size=dataset_size,
        rows=len(df),
        cpu_time=cpu_time,
    )

# =====================================================
# Workload 4 - Department Operations Summary
# =====================================================

def department_operations_summary(df):

    return (

        df.groupby("department")

        .agg(

            total_patients=("patient_id", "count"),

            average_wait=("wait_time_min", "mean"),

            critical_patients=("is_critical", "sum"),

            admissions=("admitted", "sum"),

        )

        .reset_index()

    )


def run_department_summary_cpu(dataset_size):

    df = load_benchmark_dataset(dataset_size)

    _, cpu_time = measure_execution(

        department_operations_summary,

        df,

    )

    return build_result(

        workload_name="Department Operations Summary",

        dataset_size=dataset_size,

        rows=len(df),

        cpu_time=cpu_time,

    )

# =====================================================
# Workload 5 - Risk Pipeline
# =====================================================

def risk_pipeline(df):

    df = engineer_features(df)

    df = calculate_risk(df)

    return df


def run_risk_pipeline_cpu(dataset_size):

    df = load_benchmark_dataset(dataset_size)

    _, cpu_time = measure_execution(

        risk_pipeline,

        df,

    )

    return build_result(

        workload_name="Risk Pipeline",

        dataset_size=dataset_size,

        rows=len(df),

        cpu_time=cpu_time,

    )

# =====================================================
# Workload 6 - Recommendation Generation
# =====================================================

def recommendation_generation(df):

    return generate_recommendations(df)


def run_recommendation_cpu(dataset_size):

    df = load_benchmark_dataset(dataset_size)

    _, cpu_time = measure_execution(

        recommendation_generation,

        df,

    )

    return build_result(

        workload_name="Recommendation Generation",

        dataset_size=dataset_size,

        rows=len(df),

        cpu_time=cpu_time,

    )

# =====================================================
# Workload 7 - Full Analytics Pipeline
# =====================================================

def full_pipeline(df):

    return run_pipeline(df)


def run_full_pipeline_cpu(dataset_size):

    df = load_benchmark_dataset(dataset_size)

    _, cpu_time = measure_execution(

        full_pipeline,

        df,

    )

    return build_result(

        workload_name="Full Analytics Pipeline",

        dataset_size=dataset_size,

        rows=len(df),

        cpu_time=cpu_time,

    )


# =====================================================
# Benchmark Workload Registry
# =====================================================

CPU_WORKLOADS = {
    "Patient Lookup": run_patient_lookup_cpu,
    "Department Patient Lookup": run_department_lookup_cpu,
    "Department Operations Summary": run_department_summary_cpu,
    "Risk Pipeline": run_risk_pipeline_cpu,
    "Recommendation Generation": run_recommendation_cpu,
    "Full Analytics Pipeline": run_full_pipeline_cpu,
}