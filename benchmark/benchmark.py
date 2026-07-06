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