import pandas as pd
import streamlit as st

from dashboard.config import CSV_DIR


@st.cache_data
def load_csv(name: str, required: bool = True) -> pd.DataFrame:
    path = CSV_DIR / name
    if not path.exists():
        if required:
            raise FileNotFoundError(f"Missing dashboard input: {path}")
        return pd.DataFrame()
    return pd.read_csv(path)


@st.cache_data
def load_data() -> dict[str, pd.DataFrame]:
    files = {
        "funnel": "product_funnel.csv",
        "channel": "funnel_by_acquisition_channel.csv",
        "repeat_channel": "d30_repeat_by_channel.csv",
        "cohort": "cohort_retention.csv",
        "feature": "feature_adoption.csv",
        "feature_retention": "feature_retention_comparison.csv",
        "ab_results": "ab_test_results.csv",
        "ab_segments": "ab_test_segment_results.csv",
        "model_metrics": "user_repeat_model_metrics.csv",
        "importance": "user_repeat_feature_importance.csv",
        "targeting": "user_repeat_targeting_dataset.csv",
        "campaign": "campaign_sensitivity_analysis.csv",
        "fx_metrics": "fx_volatility_model_metrics.csv",
        "fx_predictions": "fx_volatility_predictions.csv",
        "fx_behavior": "fx_regime_behavior.csv",
        "fx_source": "fx_data_source.csv",
        "quality_summary": "data_quality_summary.csv",
        "quality_issues": "data_quality_issues.csv",
    }
    return {key: load_csv(file) for key, file in files.items()}
