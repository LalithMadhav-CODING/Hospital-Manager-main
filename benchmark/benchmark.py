"""
benchmark.py

Benchmark Engine for ER Surge Intelligence.

This module provides reusable benchmarking utilities for measuring
operational workloads. It is intentionally independent of Streamlit,
BigQuery, and RAPIDS so that the same interface can benchmark both
CPU (Pandas) and GPU (cuDF) implementations.
"""

from dataclasses import dataclass, asdict
from time import perf_counter
from typing import Callable, Any
import pandas as pd
from backend.dashboard import build_dashboard
from backend.pipeline import run_pipeline
from backend.patient_service import get_dashboard


# ==========================================================
# Benchmark Result
# ==========================================================

@dataclass
class BenchmarkResult:
    workload: str
    backend: str
    rows: int
    execution_time: float
    rows_per_second: float

    def to_dict(self):
        return asdict(self)


# ==========================================================
# Benchmark Engine
# ==========================================================

class BenchmarkEngine:

    def run(
        self,
        workload_name: str,
        backend: str,
        dataframe: pd.DataFrame,
        workload: Callable[..., Any],
        *args,
        **kwargs,
    ) -> BenchmarkResult:
        """
        Execute a workload and measure execution time.
        """

        start = perf_counter()

        workload(
            dataframe,
            *args,
            **kwargs,
        )

        end = perf_counter()

        execution_time = end - start

        rows = len(dataframe)

        rows_per_second = (
            rows / execution_time
            if execution_time > 0
            else 0
        )

        return BenchmarkResult(
            workload=workload_name,
            backend=backend,
            rows=rows,
            execution_time=execution_time,
            rows_per_second=rows_per_second,
        )


# ==========================================================
# Utilities
# ==========================================================

def compare(cpu: BenchmarkResult,
            gpu: BenchmarkResult) -> dict:
    """
    Compare CPU and GPU benchmark results.
    """

    speedup = (
        cpu.execution_time / gpu.execution_time
        if gpu.execution_time > 0
        else 0
    )

    return {
        "workload": cpu.workload,
        "rows": cpu.rows,
        "cpu_time": cpu.execution_time,
        "gpu_time": gpu.execution_time,
        "cpu_rows_per_second": cpu.rows_per_second,
        "gpu_rows_per_second": gpu.rows_per_second,
        "speedup": speedup,
    }

# ==========================================================
# Operational Workloads
# ==========================================================

def patient_lookup(
    dataframe: pd.DataFrame,
    patient_id: str,
) -> pd.DataFrame:
    """
    Benchmark workload:
    Retrieve a patient using Patient ID.
    """

    result = dataframe.loc[
        dataframe["patient_id"] == patient_id
    ]

    return result

def department_patient_lookup(
    dataframe: pd.DataFrame,
    department: str,
) -> pd.DataFrame:
    """
    Benchmark workload:
    Retrieve all patients belonging
    to a department.
    """

    return dataframe.loc[
        dataframe["department"] == department
    ]

def critical_patient_queue(
    dataframe: pd.DataFrame,
    minimum_wait: int = 30,
) -> pd.DataFrame:
    """
    Benchmark workload:

    Retrieve every critical patient
    waiting longer than the specified
    threshold.
    """

    return dataframe.loc[
        (dataframe["is_critical"] == True)
        &
        (dataframe["wait_time_min"] >= minimum_wait)
    ]

def department_operations_summary(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Benchmark workload.

    Execute the production dashboard
    aggregation exactly as the
    application does.
    """

    return build_dashboard(dataframe)

def risk_pipeline(
    dataframe: pd.DataFrame,
):
    """
    Benchmark workload.

    Execute the complete production
    analytics pipeline.

    This includes:

    - Feature Engineering
    - Risk Calculation
    - Dashboard Generation
    - Recommendation Generation
    """

    return run_pipeline(dataframe)

def dashboard_refresh(
    dataframe: pd.DataFrame = None,
):
    """
    Benchmark workload.

    Execute the production dashboard
    refresh workflow exactly as the
    application does.

    Workflow:

    BigQuery
        ↓
    load_patients()
        ↓
    run_pipeline()
        ↓
    Dashboard
        ↓
    Recommendations
    """

    return get_dashboard()