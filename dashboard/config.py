from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CSV_DIR = PROJECT_ROOT / "outputs" / "csv"

PAGES = [
    "Executive Summary",
    "Funnel and Retention",
    "Feature Adoption and Simulated A/B Test",
    "Prediction and Targeting",
    "FX Market Readiness",
    "Data Quality and Methodology",
]

COLORS = {
    "navy": "#23415F",
    "teal": "#287D78",
    "orange": "#C47A34",
    "rose": "#A85D70",
    "gray": "#667085",
}
