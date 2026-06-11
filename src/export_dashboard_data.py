from pathlib import Path
import argparse
import sqlite3
import time
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "data" / "fx_fintech_product_analytics.db"
SQL_DIR = PROJECT_ROOT / "sql"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "csv"

EXPORTS = {
    "product_funnel.csv": "06_product_funnel.sql",
    "funnel_by_acquisition_channel.csv": "07_funnel_by_acquisition_channel.sql",
    "d30_repeat_by_channel.csv": "08_d30_repeat_by_channel.sql",
    "feature_retention_comparison.csv": "09_feature_retention_comparison.sql",
    "feature_combination_retention.csv": "10_feature_combination_retention.sql",
    "fx_regime_behavior.csv": "11_fx_regime_behavior.sql",
    "fx_regime_normalized_activity.csv": "12_fx_regime_normalized_activity.sql",
    "failure_reason_by_regime.csv": "13_failure_reason_by_regime.sql",
    "monthly_product_trend.csv": "14_monthly_product_trend.sql",
    "cohort_retention.csv": "15_cohort_retention.sql",
    "customer_value_segmentation.csv": "16_customer_value_segmentation.sql",
    "support_ticket_impact.csv": "17_support_ticket_impact.sql",
    "modeling_table_check.csv": "18_modeling_table_check.sql",
}

CUSTOM_QUERIES = {
    "user_lifecycle_summary.csv": """
        SELECT
            COUNT(*) AS users,
            SUM(onboarding_valid_flag) AS valid_onboarding_users,
            SUM(activation_flag) AS activated_within_14_days,
            ROUND(
                100.0 * SUM(activation_flag) / NULLIF(SUM(onboarding_valid_flag), 0),
                2
            ) AS activation_rate_14d,
            ROUND(AVG(activation_days_exact), 2) AS avg_activation_days,
            SUM(target_rate_user_flag) AS target_rate_users,
            SUM(rate_alert_user_flag) AS rate_alert_users
        FROM mart_user_lifecycle
        WHERE onboarding_valid_flag = 1;
    """
}

def read_sql_file(file_name: str) -> str:
    sql_path = SQL_DIR / file_name

    if not sql_path.exists():
        raise FileNotFoundError(f"Missing SQL file: {sql_path}")

    return sql_path.read_text(encoding="utf-8")


def export_query(
    conn: sqlite3.Connection,
    query: str,
    output_path: Path,
    overwrite: bool = False,
) -> None:
    if output_path.exists() and not overwrite:
        print(f"SKIP existing file: {output_path}")
        return

    start = time.perf_counter()

    df = pd.read_sql_query(query, conn)
    df.to_csv(output_path, index=False)

    elapsed = time.perf_counter() - start
    print(f"EXPORTED {output_path.name}: {len(df):,} rows in {elapsed:.1f}s")


def main(overwrite: bool = False) -> None:
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found: {DB_PATH}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    db_uri = f"file:{DB_PATH.as_posix()}?mode=ro"

    with sqlite3.connect(db_uri, uri=True) as conn:
        for output_file, sql_file in EXPORTS.items():
            query = read_sql_file(sql_file)
            export_query(
                conn=conn,
                query=query,
                output_path=OUTPUT_DIR / output_file,
                overwrite=overwrite,
            )

        for output_file, query in CUSTOM_QUERIES.items():
            export_query(
                conn=conn,
                query=query,
                output_path=OUTPUT_DIR / output_file,
                overwrite=overwrite,
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Export dashboard-ready CSV files from the FX fintech SQLite database."
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing CSV files in outputs/csv.",
    )

    args = parser.parse_args()
    main(overwrite=args.overwrite)
