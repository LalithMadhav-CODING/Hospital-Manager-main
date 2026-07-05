from pathlib import Path

# --------------------------------------------------
# Project Paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"

CREDENTIALS_DIR = PROJECT_ROOT / "credentials"

SERVICE_ACCOUNT = CREDENTIALS_DIR / "service_account.json"

# --------------------------------------------------
# BigQuery
# --------------------------------------------------

DATASET = "hospital_er"

TABLE = "patients"

# --------------------------------------------------
# Processing
# --------------------------------------------------

USE_CUDF = False

# --------------------------------------------------
# Department Capacities
# --------------------------------------------------

DEPARTMENT_BED_CAPACITY = {
    "Cardiology": 500,       
    "Gastroenterology": 300,  
    "General ER": 300,        
    "General Practice": 350,  
    "Neurology": 280,         
    "Orthopedics": 350,       
    "Pediatrics": 600,        
    "Renal": 320,            
}

# --------------------------------------------------
# Risk Weights
# --------------------------------------------------

RISK_WEIGHTS = {
    "wait": 0.30,
    "load": 0.30,
    "acuity": 0.25,
    "complexity": 0.15,
}

# --------------------------------------------------
# Thresholds
# --------------------------------------------------

LOW_RISK = 0.40

MODERATE_RISK = 0.70

HIGH_RISK = 0.85

# --------------------------------------------------
# Simulation
# --------------------------------------------------

AUTO_REFRESH_PATIENTS = 5