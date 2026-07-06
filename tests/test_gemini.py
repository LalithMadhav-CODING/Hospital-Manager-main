from cloud.gemini import generate_operational_summary

metrics = {
    "department": "General ER",
    "patients": 118,
    "capacity_utilization": 82.4,
    "average_wait": 35.2,
    "critical_patients": 12,
    "average_risk": 0.61,
    "risk": "MODERATE",
    "priority": "Monitor",
    "actions": [
        "Monitor patient flow",
        "Prepare additional beds if required",
    ],
}

print(generate_operational_summary(metrics))