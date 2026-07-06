"""
Gemini Service

Generates operational explanations for
ER Surge Intelligence.

This module contains NO business logic.
It only converts structured operational
metrics into natural language.
"""

import os

from google import genai


MODEL_NAME = "gemini-2.5-flash"


def _build_prompt(metrics: dict) -> str:
    """
    Build the prompt sent to Gemini.
    """

    return f"""
You are an Emergency Department Operations Assistant.

You explain hospital operational metrics.

IMPORTANT RULES

- Do NOT diagnose patients.
- Do NOT provide medical advice.
- Do NOT invent values.
- Use ONLY the supplied metrics.

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

Average Operational Risk:
{metrics["average_risk"]:.2f}

Risk Level:
{metrics["risk"]}

Priority:
{metrics["priority"]}

Recommended Actions:
{", ".join(metrics["actions"])}

Generate a concise operational report.

Use EXACTLY these headings:

### Situation Summary

### Key Observations

### Operational Concerns

### Recommended Actions

Maximum 150 words.
"""


def generate_operational_summary(metrics: dict) -> str:
    """
    Generate a natural-language operational
    explanation using Gemini.
    """

    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        return "Gemini API key not configured."

    try:

        client = genai.Client(
            api_key=api_key,
        )

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=_build_prompt(metrics),
        )

        return response.text

    except Exception as e:

        return f"Gemini Error: {e}"