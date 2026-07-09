# 🏥 ER Surge Intelligence

> **An AI-Powered Emergency Department Operations Decision Support System**
>
> Built for the **Google Cloud × NVIDIA Hackathon**

---

## 📌 Overview

Emergency Departments face increasing operational pressure due to patient surges, long wait times, resource constraints, and unpredictable emergency events.

**ER Surge Intelligence** is an AI-powered operational decision support platform that helps hospital administrators monitor Emergency Department performance in real time, simulate emergency scenarios, evaluate operational risks, and receive intelligent recommendations.

Unlike traditional Hospital Management Systems, this project focuses on **operational intelligence**, enabling data-driven decisions rather than patient record management.

---

## ✨ Features

### 📊 Live Operational Dashboard

- Emergency Department KPIs
- Department-wise patient distribution
- Wait time analytics
- Capacity utilization
- Risk visualization
- Operational recommendations

---

### 📝 Patient Registration

Register new patients directly into Google BigQuery.

Automatically updates:

- Dashboard
- Department analytics
- Risk scores
- Recommendations

---

### 🚨 Emergency Scenario Simulation

Simulate real hospital situations such as:

- Routine Patient Arrival
- Patient Surge
- Critical Ambulance Arrival
- Mass Casualty Incident

Every simulation updates the analytics pipeline and visualizes operational impact.

---

### 📈 Operational Impact Feed

Each simulation generates a detailed execution summary showing:

- Actions performed
- Timestamped operational events
- Hospital impact
- Capacity changes
- Risk transitions

---

### 🤖 AI Operational Assistant

Powered by **Google Gemini**.

Generates:

- Situation Summary
- Operational Concerns
- Key Observations
- Recommended Actions

Based solely on current operational metrics.

---

### ⚡ GPU Benchmark Framework

Benchmark analytics workloads using:

- CPU (Pandas)
- GPU (NVIDIA RAPIDS cuDF)

Supported workloads include:

- Patient Lookup
- Department Lookup
- Critical Patient Queue
- Department Operations Summary
- Risk Pipeline
- Recommendation Generation
- Full Analytics Pipeline

Benchmark datasets:

- 10K
- 20K
- 50K
- 100K
- 250K
- 500K
- 1M rows

---

# 🏗 System Architecture

> *(Insert Architecture Diagram Here)*

---

# ⚙ Technology Stack

## Frontend

- Streamlit

## Backend

- Python
- Pandas

## Cloud

- Google BigQuery
- Google Gemini

## AI

- Google Gemini 2.5 Flash

## GPU Acceleration

- NVIDIA RAPIDS
- cuDF

---

# 📂 Project Structure

```text
app.py

backend/
    loader.py
    features.py
    risk.py
    dashboard.py
    recommendations.py
    patient_service.py
    pipeline.py
    simulate.py
    utils.py

benchmark/
    benchmark.py

cloud/
    bigquery.py
    gemini.py
    storage.py
```

---

# 🔄 Application Workflow

```text
Patient Data

↓

BigQuery

↓

Feature Engineering

↓

Risk Engine

↓

Dashboard Analytics

↓

Operational Recommendations

↓

Gemini AI Summary

↓

Streamlit Dashboard
```

---

# 📊 Benchmark Workflow

```text
Benchmark Dataset

↓

Selected Workload

↓

CPU (Pandas)

↓

GPU (RAPIDS)

↓

Performance Comparison
```

---

# ☁ Google Cloud Services Used

- Google BigQuery
- Google Gemini API
- Cloud Run *(Deployment Target)*

---

# 🚀 NVIDIA Technologies

- RAPIDS
- cuDF

---

# 🖼 Screenshots

## Dashboard

> *(Insert Screenshot)*

---

## Simulation

> *(Insert Screenshot)*

---

## Gemini Insights

> *(Insert Screenshot)*

---

## Benchmark

> *(Insert Screenshot)*

---

# 🚀 Getting Started

## Clone

```bash
git clone <repository-url>
```

---

## Install

```bash
pip install -r requirements.txt
```

---

## Run

```bash
streamlit run app.py
```

---

# 🌟 Future Work

- Real-time streaming analytics
- Multi-hospital monitoring
- Predictive patient surge forecasting
- Bed allocation optimization
- GPU-enabled cloud benchmarking
- LLM-powered operational planning

---

# 👨‍💻 Team

FireForceDeva

---

# 📄 License

MIT License