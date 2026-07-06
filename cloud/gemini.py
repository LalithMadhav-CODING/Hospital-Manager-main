"""
Gemini Service

This module is responsible only for generating
natural language explanations of the operational
state of the Emergency Department.

No business logic should exist here.
"""

import os

import google.generativeai as genai


# --------------------------------------------------
# Configure Gemini
# --------------------------------------------------

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)


MODEL_NAME = "gemini-2.5-flash"


# --------------------------------------------------
# Prompt Builder
# --------------------------------------------------

def _build_prompt(metrics: dict) -> str:
    """
    Convert structured operational metrics
    into a prompt for Gemini.
    """

    return f"""
You are an Emergency Department Operations Assistant.

IMPORTANT:

- Do NOT provide medical advice.
- Do NOT diagnose patients.
- Do NOT invent values.
- Use ONLY the supplied operational metrics.
- Focus only on hospital operations.

Department:
{metrics["department"]}

Patients:
{metrics["patients"]}

Capacity Utilization:
{metrics["capacity_utilization"]:.1f}%

Average Wait:
{metrics["average_wait"]:.1f} minutes

Critical Patients:
{metrics["critical_patients"]}

Average Risk:
{metrics["average_risk"]:.2f}

Risk Level:
{metrics["risk"]}

Priority:
{metrics["priority"]}

Recommended Actions:
{", ".join(metrics["actions"])}

Write a concise operational report.

Format:

Situation Summary

Key Observations

Operational Concerns

Recommended Actions

Keep the response under 150 words.
"""


# --------------------------------------------------
# Public API
# --------------------------------------------------

def generate_operational_summary(metrics: dict) -> str:
    """
    Generate an operational explanation
    using Gemini.
    """

    if not GOOGLE_API_KEY:
        return (
            "Gemini API key not configured."
        )

    model = genai.GenerativeModel(MODEL_NAME)

    response = model.generate_content(
        _build_prompt(metrics)
    )

    return response.text