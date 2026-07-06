import pandas as pd

from benchmark.benchmark import (
    BenchmarkEngine,
    patient_lookup,
)

df = pd.DataFrame({
    "patient_id": [
        "P000001",
        "P000002",
        "P000003",
    ],
    "age": [25, 40, 60],
})

engine = BenchmarkEngine()

result = engine.run(
    workload_name="Patient Lookup",
    backend="CPU",
    dataframe=df,
    workload=patient_lookup,
    patient_id="P000002",
)

print(result.to_dict())