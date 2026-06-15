from pathlib import Path
import sqlite3

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "data" / "fx_fintech_product_analytics.db"
CSV_DIR = PROJECT_ROOT / "outputs" / "csv"

PREDICTION_PATH = CSV_DIR / "user_repeat_predictions.csv"
OUTPUT_PATH = CSV_DIR / "user_repeat_targeting_dataset.csv"

FEE_RATE_PROXY = 0.00025


def load_predictions() -> pd.DataFrame:
    if not PREDICTION_PATH.exists():
        raise FileNotFoundError(f"Missing prediction file: {PREDICTION_PATH}")

    predictions = pd.read_csv(PREDICTION_PATH)
    predictions["observation_date"] = pd.to_datetime(predictions["observation_date"])
    return predictions


def load_snapshot_features() -> pd.DataFrame:
    query = """
        SELECT
            user_id,
            observation_date,
            recency_days,
            transactions_90d,
            transactions_all,
            total_volume_90d,
            failed_ratio_90d
        FROM modeling_user_month_snapshots;
    """

    with sqlite3.connect(DB_PATH) as conn:
        snapshots = pd.read_sql_query(query, conn)

    snapshots["observation_date"] = pd.to_datetime(snapshots["observation_date"])
    return snapshots


def load_lifecycle_features() -> pd.DataFrame:
    query = """
        SELECT
            user_id,
            acquisition_channel,
            successful_transaction_count,
            successful_transaction_volume,
            target_rate_user_flag,
            rate_alert_user_flag
        FROM mart_user_lifecycle;
    """

    with sqlite3.connect(DB_PATH) as conn:
        lifecycle = pd.read_sql_query(query, conn)

    return lifecycle


def assign_probability_segment(probability: float) -> str:
    if probability < 0.35:
        return "Low repeat probability"
    if probability < 0.70:
        return "Medium repeat probability"
    return "High repeat probability"


def assign_value_segment(volume: float, high_value_threshold: float) -> str:
    if volume >= high_value_threshold:
        return "High value"
    if volume > 0:
        return "Active value"
    return "No recent value"


def assign_risk_segment(row: pd.Series) -> str:
    if row["value_segment"] == "High value" and row["repeat_probability"] < 0.50:
        return "High-value at-risk users"
    if row["transactions_90d"] == 0:
        return "No recent transaction users"
    if row["failed_ratio_90d"] >= 0.15:
        return "High failed-ratio users"
    if row["repeat_probability"] < 0.35:
        return "Low repeat probability users"
    if row["repeat_probability"] < 0.70:
        return "Medium repeat probability users"
    return "High repeat probability users"


def recommend_action(row: pd.Series) -> tuple[str, str]:
    no_feature_adoption = (
        row["target_rate_user_flag"] == 0
        and row["rate_alert_user_flag"] == 0
    )

    if row["value_segment"] == "High value" and row["repeat_probability"] < 0.50:
        return (
            "Priority retention outreach",
            "High recent volume but repeat probability is below 50%.",
        )

    if row["failed_ratio_90d"] >= 0.15:
        return (
            "Reliability support message",
            "Recent failed transaction ratio is elevated.",
        )

    if row["repeat_probability"] < 0.35 and row["transactions_90d"] == 0:
        return (
            "Reactivation education campaign",
            "Low repeat probability and no transaction activity in the last 90 days.",
        )

    if row["repeat_probability"] < 0.35:
        return (
            "Reactivation offer",
            "Low repeat probability despite some historical product activity.",
        )

    if row["repeat_probability"] < 0.70 and no_feature_adoption:
        return (
            "Rate-alert prompt",
            "Medium repeat probability and no target-rate or rate-alert adoption yet.",
        )

    if row["repeat_probability"] < 0.70 and row["rate_alert_user_flag"] == 0:
        return (
            "Promote rate-alert adoption",
            "Medium repeat probability and rate-alert feature has not been adopted.",
        )

    if row["repeat_probability"] >= 0.70 and row["target_rate_user_flag"] == 0:
        return (
            "Target-rate upsell",
            "High repeat probability and target-rate feature has not been adopted.",
        )

    return (
        "Maintain engagement",
        "User already has strong repeat probability or feature engagement.",
    )


def build_targeting_dataset() -> pd.DataFrame:
    predictions = load_predictions()
    snapshots = load_snapshot_features()
    lifecycle = load_lifecycle_features()

    enriched = predictions.merge(
        snapshots,
        on=["user_id", "observation_date"],
        how="left",
        validate="one_to_one",
    )
    enriched = enriched.merge(
        lifecycle,
        on="user_id",
        how="left",
        validate="many_to_one",
    )

    high_value_threshold = enriched["total_volume_90d"].quantile(0.75)

    enriched["probability_segment"] = enriched["repeat_probability"].map(
        assign_probability_segment
    )
    enriched["value_segment"] = enriched["total_volume_90d"].map(
        lambda volume: assign_value_segment(volume, high_value_threshold)
    )
    enriched["risk_segment"] = enriched.apply(assign_risk_segment, axis=1)

    recommendations = enriched.apply(recommend_action, axis=1)
    enriched["recommended_action"] = recommendations.map(lambda item: item[0])
    enriched["recommendation_reason"] = recommendations.map(lambda item: item[1])

    enriched["estimated_fee_proxy_90d"] = (
        enriched["total_volume_90d"].fillna(0) * FEE_RATE_PROXY
    )

    ordered_columns = [
        "user_id",
        "observation_date",
        "target_repeat_30d",
        "repeat_probability",
        "predicted_repeat_30d",
        "probability_segment",
        "risk_segment",
        "recommended_action",
        "recommendation_reason",
        "recency_days",
        "transactions_90d",
        "transactions_all",
        "total_volume_90d",
        "estimated_fee_proxy_90d",
        "failed_ratio_90d",
        "value_segment",
        "acquisition_channel",
        "successful_transaction_count",
        "successful_transaction_volume",
        "target_rate_user_flag",
        "rate_alert_user_flag",
    ]

    return enriched[ordered_columns].sort_values(
        ["repeat_probability", "total_volume_90d"],
        ascending=[False, False],
    )


def main() -> None:
    CSV_DIR.mkdir(parents=True, exist_ok=True)
    targeting_dataset = build_targeting_dataset()
    targeting_dataset.to_csv(OUTPUT_PATH, index=False)

    print(f"Exported {OUTPUT_PATH}")
    print(f"Rows: {len(targeting_dataset):,}")
    print("Columns:")
    for column in targeting_dataset.columns:
        print(f"- {column}")


if __name__ == "__main__":
    main()
