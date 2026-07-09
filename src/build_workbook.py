from pathlib import Path

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "notebooks" / "00_fx_fintech_product_analytics_workbook.ipynb"


def markdown(text: str):
    return nbf.v4.new_markdown_cell(text)


def code(text: str):
    return nbf.v4.new_code_cell(text)


cells = [
    markdown("# FX Fintech Product Analytics Workbook\n\nSynthetic product behavior is combined with historical Yahoo Finance FX observations. Product results are illustrative, not production evidence."),
    markdown("## 0.1 Import Libraries"),
    code(
        """from pathlib import Path
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

PROJECT_ROOT = Path.cwd().resolve()
if PROJECT_ROOT.name == "notebooks":
    PROJECT_ROOT = PROJECT_ROOT.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.analytics_workflow import (
    CSV_DIR, build_data_mart, dataset_overview, export_product_analysis,
    project_setup, run_campaign_simulator, run_data_quality_checks,
    run_fx_readiness_model, run_simulated_ab_test, train_repeat_models,
)
pd.set_option("display.max_columns", 30)"""
    ),
    markdown("## 0.2 Project Configuration"),
    code(
        """project_setup()
build_data_mart()
print(f"Project root: {PROJECT_ROOT}")
print("Random seed: 42")
print("Product source: synthetic SQLite database")
print("FX model source: cached Yahoo Finance historical data")"""
    ),
    markdown("## 1.1 Dataset Overview\n\nThe SQLite product tables are synthetic. The legacy hourly FX table is simulated and is not used to train the volatility model; that model uses a cached Yahoo Finance snapshot."),
    code("overview = dataset_overview()\noverview"),
    markdown("## 1.2 Data Quality Checks\n\nChecks distinguish invalid records from expected optional fields and review-only outliers."),
    code("quality_summary, quality_issues = run_data_quality_checks()\nquality_summary"),
    code("quality_issues[quality_issues['issue_count'] > 0]"),
    markdown("## 1.3 Product Funnel Analysis\n\nActivation requires KYC, bank link, and a first successful exchange within 14 days."),
    code("product_outputs = export_product_analysis()\nfunnel = product_outputs['product_funnel.csv']\nfunnel"),
    markdown("## 1.4 Cohort Retention Analysis\n\nMonthly retention starts from each user's first successful exchange month."),
    code(
        """cohort = product_outputs["cohort_retention.csv"]
cohort_pivot = cohort[cohort["months_since_first_transaction"].between(1, 6)].pivot(
    index="cohort_month", columns="months_since_first_transaction", values="retention_rate"
)
cohort_pivot.tail(12)"""
    ),
    markdown("## 1.5 Feature Adoption Analysis\n\nAdoption is descriptive. It does not establish that feature use causes retention."),
    code("feature_adoption = product_outputs['feature_adoption.csv']\nfeature_adoption"),
    code("product_outputs['feature_retention_comparison.csv']"),
    markdown("## 1.6 Acquisition Channel Quality\n\nChannel quality combines activation and D30 repeat behavior rather than signup volume alone."),
    code(
        """channel_quality = product_outputs["funnel_by_acquisition_channel.csv"].merge(
    product_outputs["d30_repeat_by_channel.csv"], on="acquisition_channel", how="left"
)
channel_quality.sort_values(["activation_rate_14d", "d30_repeat_rate"], ascending=False)"""
    ),
    markdown("## 2.1 User Repeat Prediction\n\nFeatures summarize the trailing 90 days through each observation date. The target is repeat behavior in the following 30 days."),
    code(
        """modeling_check = product_outputs["modeling_table_check.csv"]
modeling_check"""
    ),
    markdown("## 2.2 Model Training and Comparison\n\nThe split is chronological. Optional libraries are included only when installed."),
    code("repeat_results = train_repeat_models()\nrepeat_results['metrics']"),
    markdown("## 2.3 Model Evaluation\n\nSelection balances ranking, positive-class performance, reliability, and explanation cost."),
    code(
        """selected_repeat_model = repeat_results["selected_model"]
print(selected_repeat_model)
print(repeat_results["selection_rationale"])
pd.read_csv(CSV_DIR / "user_repeat_confusion_matrix.csv")"""
    ),
    code("pd.read_csv(CSV_DIR / 'user_repeat_classification_report.csv')"),
    markdown("## 2.4 Feature Importance\n\nImportance explains model dependence, not causal effect."),
    code("pd.read_csv(CSV_DIR / 'user_repeat_feature_importance.csv')"),
    markdown("## 2.5 Prediction-to-Action Mapping\n\nRules convert scores and operational context into testable CRM actions."),
    code(
        """targeting = repeat_results["targeting"]
targeting.groupby(["risk_segment", "recommended_action"], as_index=False).agg(
    users=("user_id", "count"),
    avg_repeat_probability=("repeat_probability", "mean"),
).sort_values("users", ascending=False)"""
    ),
    markdown("## 3.1 FX Volatility Regime Analysis\n\nHistorical transaction behavior is compared across the existing market-regime labels."),
    code("product_outputs['fx_regime_behavior.csv']"),
    markdown("## 3.2 FX Volatility Prediction\n\nHistorical Yahoo Finance observations are cached locally. A time split predicts the next day's volatility regime from lagged FX features; this is not an exchange-rate forecast."),
    code("fx_results = run_fx_readiness_model()\nfx_results['source']"),
    code("fx_results['metrics']"),
    markdown("## 3.3 Operational Readiness Signal\n\nThe signal supports staffing, transaction monitoring, rate-change messaging, and campaign timing."),
    code("fx_results['predictions'].tail(10)"),
    markdown("## 4.1 Campaign Targeting Logic\n\nPriority rules identify service recovery, reactivation, transaction-friction, and controlled-test audiences."),
    code(
        """targeting.groupby("risk_segment", as_index=False).agg(
    users=("user_id", "count"),
    avg_repeat_probability=("repeat_probability", "mean"),
    recent_volume_krw=("total_volume_90d", "sum"),
).sort_values("users", ascending=False)"""
    ),
    markdown("## 4.2 Campaign Simulator\n\nLow, base, and high assumptions show sensitivity. Fee impact is a value proxy, not revenue."),
    code("campaign_base, campaign_sensitivity = run_campaign_simulator(targeting)\ncampaign_base"),
    code("campaign_sensitivity"),
    markdown("## 5.1 A/B Test Design\n\nNo production experiment table exists. Assignment and outcomes are simulated to demonstrate analysis logic, not causal evidence."),
    code("ab_design, ab_results, ab_segments = run_simulated_ab_test()\nab_design"),
    markdown("## 5.2 A/B Test Statistical Evaluation\n\nReport confidence intervals, p-values, and practical significance together."),
    code("ab_results"),
    code("ab_segments.sort_values('absolute_uplift', ascending=False)"),
    markdown("## 6.1 Dashboard Export Files\n\nAll dashboard inputs are written to `outputs/csv/`; trained models are written to `models/`."),
    code(
        """exports = pd.DataFrame({
    "file": [path.name for path in sorted(CSV_DIR.glob("*.csv"))],
    "size_kb": [round(path.stat().st_size / 1024, 1) for path in sorted(CSV_DIR.glob("*.csv"))],
})
exports"""
    ),
    markdown(
        "## 6.2 Limitations and Next Steps\n\n"
        "- Product behavior is synthetic; findings do not represent company performance.\n"
        "- FX prices are historical Yahoo Finance observations, subject to provider availability and adjustments.\n"
        "- Feature adoption comparisons are observational and may reflect user intent.\n"
        "- The experiment is simulated and must not be presented as production causal evidence.\n"
        "- Fee impact is an assumption-based proxy, not reported revenue.\n"
        "- Next steps are production metric validation, experiment instrumentation, probability calibration, and drift monitoring."
    ),
]

notebook = nbf.v4.new_notebook(
    cells=cells,
    metadata={
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.10"},
    },
)
nbf.write(notebook, OUTPUT)
print(f"Wrote {OUTPUT}")
