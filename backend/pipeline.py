from backend.loader import load_er_data
from backend.features import engineer_features
from backend.risk import calculate_risk
from backend.dashboard import build_dashboard
from backend.recommendations import generate_recommendations


def run_pipeline(df=None):

    if df is None:
        df = load_er_data()

    df = engineer_features(df)

    df = calculate_risk(df)

    dashboard = build_dashboard(df)

    recommendation = generate_recommendations(dashboard)

    return df, dashboard, recommendation