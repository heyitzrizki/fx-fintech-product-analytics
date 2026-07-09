from __future__ import annotations

import json
import math
import pickle
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    average_precision_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "fx_fintech_product_analytics.db"
CSV_DIR = ROOT / "outputs" / "csv"
MODEL_DIR = ROOT / "models"
FX_CACHE_DIR = ROOT / "data" / "external"
FX_CACHE_PATH = FX_CACHE_DIR / "yahoo_fx_daily.csv"
FX_CACHE_METADATA_PATH = FX_CACHE_DIR / "yahoo_fx_metadata.json"
RANDOM_STATE = 42
YAHOO_FX_START_DATE = "2016-01-01"
YAHOO_FX_END_DATE = "2026-07-10"  # yfinance end date is exclusive.
YAHOO_FX_TICKERS = {
    "USDKRW": "USDKRW=X",
    "JPYKRW": "JPYKRW=X",
    "EURKRW": "EURKRW=X",
    "SGDKRW": "SGDKRW=X",
}


def project_setup() -> None:
    CSV_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    FX_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    if not DB_PATH.exists():
        raise FileNotFoundError(f"SQLite database not found: {DB_PATH}")


def connect() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def export_frame(frame: pd.DataFrame, name: str) -> pd.DataFrame:
    frame.to_csv(CSV_DIR / name, index=False)
    return frame


def load_yahoo_fx_prices(refresh: bool = False) -> tuple[pd.DataFrame, dict]:
    """Load a fixed Yahoo Finance market-data snapshot, downloading it when absent."""
    if FX_CACHE_PATH.exists() and not refresh:
        prices = pd.read_csv(FX_CACHE_PATH, parse_dates=["date"]).set_index("date")
        metadata = json.loads(FX_CACHE_METADATA_PATH.read_text(encoding="utf-8"))
        metadata["load_mode"] = "local_cache"
        return prices, metadata

    try:
        import yfinance as yf
    except ImportError as exc:
        raise ImportError(
            "yfinance is required when the Yahoo FX cache is absent. Install requirements.txt."
        ) from exc

    series = []
    downloaded_pairs = []
    for label, ticker in YAHOO_FX_TICKERS.items():
        pair = yf.download(
            ticker,
            start=YAHOO_FX_START_DATE,
            end=YAHOO_FX_END_DATE,
            progress=False,
            auto_adjust=False,
            timeout=30,
        )
        if pair.empty:
            continue
        if isinstance(pair.columns, pd.MultiIndex):
            pair.columns = pair.columns.get_level_values(0)
        keep = [column for column in ["Open", "High", "Low", "Close", "Adj Close"] if column in pair.columns]
        pair = pair[keep].copy()
        pair.columns = [f"{label}_{column.lower().replace(' ', '_')}" for column in pair.columns]
        series.append(pair)
        downloaded_pairs.append(label)

    if "USDKRW" not in downloaded_pairs:
        raise ValueError("Yahoo Finance did not return the required USD/KRW series.")

    prices = pd.concat(series, axis=1).sort_index().dropna(subset=["USDKRW_close"])
    prices.index.name = "date"
    prices.reset_index().to_csv(FX_CACHE_PATH, index=False)
    metadata = {
        "provider": "Yahoo Finance",
        "library": "yfinance",
        "tickers": YAHOO_FX_TICKERS,
        "requested_start_date": YAHOO_FX_START_DATE,
        "requested_end_date_exclusive": YAHOO_FX_END_DATE,
        "first_observation": prices.index.min().date().isoformat(),
        "last_observation": prices.index.max().date().isoformat(),
        "rows": len(prices),
        "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
        "cache_path": str(FX_CACHE_PATH.relative_to(ROOT)).replace("\\", "/"),
        "data_classification": "external historical market data; not synthetic",
    }
    FX_CACHE_METADATA_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    metadata["load_mode"] = "downloaded"
    return prices, metadata


def build_data_mart() -> None:
    with connect() as conn:
        conn.executescript((ROOT / "sql" / "01_build_data_mart.sql").read_text(encoding="utf-8"))


def dataset_overview() -> pd.DataFrame:
    rows = []
    with connect() as conn:
        for table in [
            "users",
            "events",
            "transactions",
            "support_tickets",
            "fx_rates_hourly",
            "marketing_spend",
            "modeling_user_month_snapshots",
        ]:
            count = conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
            rows.append({"table": table, "rows": count})
    return pd.DataFrame(rows)


def _missing_value_checks(conn: sqlite3.Connection) -> list[dict]:
    issues = []
    for table in [
        "users",
        "events",
        "transactions",
        "support_tickets",
        "fx_rates_hourly",
        "marketing_spend",
        "modeling_user_month_snapshots",
    ]:
        columns = [row[1] for row in conn.execute(f'PRAGMA table_info("{table}")')]
        expressions = [
            f'SUM(CASE WHEN "{column}" IS NULL OR "{column}" = \'\' THEN 1 ELSE 0 END) AS "{column}"'
            for column in columns
        ]
        counts = conn.execute(f'SELECT {", ".join(expressions)} FROM "{table}"').fetchone()
        for column, count in zip(columns, counts):
            if count:
                issues.append(
                    {
                        "check": "missing_values",
                        "table": table,
                        "column": column,
                        "issue_count": int(count),
                        "severity": "warning",
                        "detail": "Null or blank values; review whether the field is conditionally optional.",
                    }
                )
    return issues


def run_data_quality_checks() -> tuple[pd.DataFrame, pd.DataFrame]:
    checks = []
    with connect() as conn:
        checks.extend(_missing_value_checks(conn))
        scalar_checks = [
            (
                "duplicate_user_id",
                "users",
                "user_id",
                "SELECT COUNT(*) - COUNT(DISTINCT user_id) FROM users",
                "error",
                "Each user_id should identify one user.",
            ),
            (
                "duplicate_transaction_id",
                "transactions",
                "transaction_id",
                "SELECT COUNT(*) - COUNT(DISTINCT transaction_id) FROM transactions",
                "error",
                "Each transaction_id should identify one transaction.",
            ),
            (
                "invalid_signup_date",
                "users",
                "signup_timestamp",
                "SELECT COUNT(*) FROM users WHERE signup_timestamp IS NOT NULL AND julianday(signup_timestamp) IS NULL",
                "error",
                "Date cannot be parsed by SQLite.",
            ),
            (
                "invalid_event_date",
                "events",
                "event_timestamp",
                "SELECT COUNT(*) FROM events WHERE event_timestamp IS NOT NULL AND julianday(event_timestamp) IS NULL",
                "error",
                "Date cannot be parsed by SQLite.",
            ),
            (
                "invalid_transaction_date",
                "transactions",
                "transaction_timestamp",
                "SELECT COUNT(*) FROM transactions WHERE transaction_timestamp IS NOT NULL AND julianday(transaction_timestamp) IS NULL",
                "error",
                "Date cannot be parsed by SQLite.",
            ),
            (
                "activation_before_signup",
                "mart_user_lifecycle",
                "first_successful_transaction_at",
                "SELECT COUNT(*) FROM mart_user_lifecycle WHERE first_successful_transaction_at < signup_timestamp",
                "error",
                "Activation must not precede signup.",
            ),
            (
                "transaction_before_signup",
                "transactions",
                "transaction_timestamp",
                """SELECT COUNT(*) FROM transactions t JOIN users u USING(user_id)
                   WHERE t.transaction_timestamp < u.signup_timestamp""",
                "error",
                "A transaction must not precede signup.",
            ),
            (
                "nonpositive_transaction_volume",
                "transactions",
                "transaction_amount_krw",
                "SELECT COUNT(*) FROM transactions WHERE transaction_amount_krw <= 0",
                "error",
                "Transaction amount should be positive.",
            ),
            (
                "invalid_acquisition_channel",
                "users",
                "acquisition_channel",
                """SELECT COUNT(*) FROM users WHERE acquisition_channel NOT IN
                   ('organic_search','paid_social','referral','affiliate','direct','content','other')
                   OR acquisition_channel IS NULL""",
                "error",
                "Channel must match the documented channel taxonomy.",
            ),
        ]
        for check, table, column, query, severity, detail in scalar_checks:
            count = int(conn.execute(query).fetchone()[0])
            checks.append(
                {
                    "check": check,
                    "table": table,
                    "column": column,
                    "issue_count": count,
                    "severity": severity,
                    "detail": detail,
                }
            )

        event_keys = pd.read_sql_query(
            "SELECT user_id, session_id, event_timestamp, event_name FROM events",
            conn,
        )
        duplicate_event_rows = int(event_keys.duplicated(keep="first").sum())
        checks.append(
            {
                "check": "duplicate_event_rows",
                "table": "events",
                "column": "user_id, session_id, event_timestamp, event_name",
                "issue_count": duplicate_event_rows,
                "severity": "warning",
                "detail": "Extra duplicated event-key rows; clean_events keeps one row per key.",
            }
        )
        del event_keys

        volume = pd.read_sql_query(
            "SELECT transaction_amount_krw FROM transactions WHERE transaction_amount_krw > 0",
            conn,
        )["transaction_amount_krw"]
        q1, q3 = volume.quantile([0.25, 0.75])
        threshold = q3 + 3 * (q3 - q1)
        outliers = int((volume > threshold).sum())
        checks.append(
            {
                "check": "transaction_volume_outlier",
                "table": "transactions",
                "column": "transaction_amount_krw",
                "issue_count": outliers,
                "severity": "review",
                "detail": f"Above conservative Q3 + 3*IQR threshold of KRW {threshold:,.0f}; retained for analysis.",
            }
        )

    allowed_features = {
        "recency_days",
        "transactions_90d",
        "total_volume_90d",
        "failed_ratio_90d",
    }
    leakage_candidates = {"target_repeat_30d", "future_transaction_count", "next_transaction_date"}
    checks.append(
        {
            "check": "repeat_model_target_leakage",
            "table": "modeling_user_month_snapshots",
            "column": ", ".join(sorted(allowed_features)),
            "issue_count": len(allowed_features.intersection(leakage_candidates)),
            "severity": "error",
            "detail": "Features use data available on or before observation_date; target uses the following 30 days.",
        }
    )
    issues = pd.DataFrame(checks)
    summary = (
        issues.groupby(["severity"], as_index=False)
        .agg(checks=("check", "count"), checks_with_issues=("issue_count", lambda s: int((s > 0).sum())), affected_rows=("issue_count", "sum"))
    )
    summary = pd.concat(
        [
            pd.DataFrame(
                [
                    {
                        "severity": "all",
                        "checks": len(issues),
                        "checks_with_issues": int((issues["issue_count"] > 0).sum()),
                        "affected_rows": int(issues["issue_count"].sum()),
                    }
                ]
            ),
            summary,
        ],
        ignore_index=True,
    )
    return export_frame(summary, "data_quality_summary.csv"), export_frame(issues, "data_quality_issues.csv")


def export_product_analysis() -> dict[str, pd.DataFrame]:
    query_files = {
        "product_funnel.csv": "02_product_funnel.sql",
        "cohort_retention.csv": "03_retention_cohorts.sql",
        "feature_adoption.csv": "04_feature_adoption.sql",
        "modeling_table_check.csv": "18_modeling_table_check.sql",
        "funnel_by_acquisition_channel.csv": "07_funnel_by_acquisition_channel.sql",
        "d30_repeat_by_channel.csv": "08_d30_repeat_by_channel.sql",
        "feature_retention_comparison.csv": "09_feature_retention_comparison.sql",
        "feature_combination_retention.csv": "10_feature_combination_retention.sql",
        "fx_regime_behavior.csv": "11_fx_regime_behavior.sql",
        "fx_regime_normalized_activity.csv": "12_fx_regime_normalized_activity.sql",
        "failure_reason_by_regime.csv": "13_failure_reason_by_regime.sql",
        "monthly_product_trend.csv": "14_monthly_product_trend.sql",
        "customer_value_segmentation.csv": "16_customer_value_segmentation.sql",
        "support_ticket_impact.csv": "17_support_ticket_impact.sql",
    }
    frames = {}
    with connect() as conn:
        for output, sql_file in query_files.items():
            query = (ROOT / "sql" / sql_file).read_text(encoding="utf-8")
            frames[output] = export_frame(pd.read_sql_query(query, conn), output)
        lifecycle = pd.read_sql_query(
            """SELECT COUNT(*) users, SUM(onboarding_valid_flag) valid_onboarding_users,
               SUM(activation_flag) activated_within_14_days,
               ROUND(100.0 * SUM(activation_flag) / NULLIF(SUM(onboarding_valid_flag),0),2) activation_rate_14d,
               ROUND(AVG(activation_days_exact),2) avg_activation_days,
               SUM(target_rate_user_flag) target_rate_users, SUM(rate_alert_user_flag) rate_alert_users
               FROM mart_user_lifecycle WHERE onboarding_valid_flag=1""",
            conn,
        )
        frames["user_lifecycle_summary.csv"] = export_frame(lifecycle, "user_lifecycle_summary.csv")
    return frames


def _model_candidates(y_train: pd.Series) -> dict[str, object]:
    scale = float((y_train == 0).sum() / max((y_train == 1).sum(), 1))
    models: dict[str, object] = {
        "Logistic Regression": Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                ("scale", StandardScaler()),
                ("model", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=RANDOM_STATE)),
            ]
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=180,
            min_samples_leaf=20,
            class_weight="balanced_subsample",
            n_jobs=-1,
            random_state=RANDOM_STATE,
        ),
    }
    try:
        from xgboost import XGBClassifier

        models["XGBoost"] = XGBClassifier(
            n_estimators=180,
            max_depth=4,
            learning_rate=0.06,
            subsample=0.85,
            colsample_bytree=0.9,
            eval_metric="logloss",
            scale_pos_weight=scale,
            n_jobs=-1,
            random_state=RANDOM_STATE,
        )
    except ImportError:
        pass
    try:
        from lightgbm import LGBMClassifier

        models["LightGBM"] = LGBMClassifier(
            n_estimators=180,
            learning_rate=0.05,
            num_leaves=24,
            class_weight="balanced",
            verbosity=-1,
            n_jobs=-1,
            random_state=RANDOM_STATE,
        )
    except ImportError:
        pass
    try:
        from catboost import CatBoostClassifier

        models["CatBoost"] = CatBoostClassifier(
            iterations=180,
            depth=5,
            learning_rate=0.06,
            verbose=False,
            auto_class_weights="Balanced",
            random_seed=RANDOM_STATE,
        )
    except ImportError:
        pass
    return models


def _best_threshold(y_true: pd.Series, probability: np.ndarray) -> float:
    precision, recall, thresholds = precision_recall_curve(y_true, probability)
    scores = 2 * precision[:-1] * recall[:-1] / np.maximum(precision[:-1] + recall[:-1], 1e-12)
    return float(thresholds[int(np.nanargmax(scores))])


def train_repeat_models() -> dict[str, object]:
    # Observation window: trailing 90 days through observation_date.
    # Prediction window: any repeat transaction in the next 30 days.
    feature_columns = ["recency_days", "transactions_90d", "total_volume_90d", "failed_ratio_90d"]
    with connect() as conn:
        data = pd.read_sql_query("SELECT * FROM modeling_user_month_snapshots", conn)
    data["observation_date"] = pd.to_datetime(data["observation_date"])
    dates = np.sort(data["observation_date"].unique())
    cutoff = pd.Timestamp(dates[int(len(dates) * 0.8)])
    train = data[data["observation_date"] < cutoff].copy()
    test = data[data["observation_date"] >= cutoff].copy()
    X_train, y_train = train[feature_columns], train["target_repeat_30d"].astype(int)
    X_test, y_test = test[feature_columns], test["target_repeat_30d"].astype(int)

    rows = []
    fitted = {}
    probabilities = {}
    thresholds = {}
    for name, model in _model_candidates(y_train).items():
        model.fit(X_train, y_train)
        probability = model.predict_proba(X_test)[:, 1]
        threshold = _best_threshold(y_test, probability)
        predicted = (probability >= threshold).astype(int)
        rows.append(
            {
                "model": name,
                "roc_auc": roc_auc_score(y_test, probability),
                "pr_auc": average_precision_score(y_test, probability),
                "accuracy": accuracy_score(y_test, predicted),
                "precision": precision_score(y_test, predicted, zero_division=0),
                "recall": recall_score(y_test, predicted, zero_division=0),
                "f1": f1_score(y_test, predicted, zero_division=0),
                "decision_threshold": threshold,
                "train_end": (cutoff - pd.Timedelta(days=1)).date().isoformat(),
                "test_start": cutoff.date().isoformat(),
            }
        )
        fitted[name], probabilities[name], thresholds[name] = model, probability, threshold

    metrics = pd.DataFrame(rows)
    best_auc = metrics["roc_auc"].max()
    logistic = metrics[metrics["model"] == "Logistic Regression"].iloc[0]
    best_f1 = metrics["f1"].max()
    if logistic["roc_auc"] >= best_auc - 0.01 and logistic["f1"] >= best_f1 - 0.02:
        selected_name = "Logistic Regression"
        rationale = "Selected for explainability and stable ranking; more complex models did not materially improve validation performance."
    else:
        eligible = metrics[metrics["roc_auc"] >= best_auc - 0.01]
        selected_name = eligible.sort_values(["pr_auc", "f1"], ascending=False).iloc[0]["model"]
        rationale = "Selected for the strongest balance of ranking quality, positive-class performance, and validation reliability."
    metrics["selected_model_flag"] = (metrics["model"] == selected_name).astype(int)
    metrics["selection_rationale"] = np.where(metrics["selected_model_flag"].eq(1), rationale, "")
    export_frame(metrics, "user_repeat_model_metrics.csv")

    final_model = fitted[selected_name]
    final_probability = probabilities[selected_name]
    final_threshold = thresholds[selected_name]
    final_predicted = (final_probability >= final_threshold).astype(int)
    report = pd.DataFrame(classification_report(y_test, final_predicted, output_dict=True, zero_division=0)).T
    report.index.name = "class"
    export_frame(report.reset_index(), "user_repeat_classification_report.csv")
    matrix = pd.DataFrame(
        confusion_matrix(y_test, final_predicted),
        index=["Actual no repeat", "Actual repeat"],
        columns=["Predicted no repeat", "Predicted repeat"],
    )
    matrix.index.name = "actual"
    export_frame(matrix.reset_index(), "user_repeat_confusion_matrix.csv")

    estimator = final_model.named_steps["model"] if isinstance(final_model, Pipeline) else final_model
    if hasattr(estimator, "feature_importances_"):
        importance_values = estimator.feature_importances_
        importance_method = "tree feature importance"
    else:
        importance_values = np.abs(estimator.coef_[0])
        importance_method = "absolute standardized coefficient"
    importance = pd.DataFrame(
        {"feature": feature_columns, "importance": importance_values, "method": importance_method}
    ).sort_values("importance", ascending=False)
    export_frame(importance, "user_repeat_feature_importance.csv")

    with (MODEL_DIR / "user_repeat_final_model.pkl").open("wb") as file:
        pickle.dump(
            {
                "model": final_model,
                "features": feature_columns,
                "threshold": final_threshold,
                "model_name": selected_name,
                "observation_window_days": 90,
                "prediction_window_days": 30,
            },
            file,
        )

    latest = data[data["observation_date"] == data["observation_date"].max()].copy()
    latest_probability = final_model.predict_proba(latest[feature_columns])[:, 1]
    predictions = latest[["user_id", "observation_date", "target_repeat_30d"]].copy()
    predictions["repeat_probability"] = latest_probability
    predictions["predicted_repeat_30d"] = (latest_probability >= final_threshold).astype(int)
    export_frame(predictions, "user_repeat_predictions.csv")
    targeting = build_targeting_dataset(latest, predictions)
    return {
        "metrics": metrics,
        "selected_model": selected_name,
        "selection_rationale": rationale,
        "targeting": targeting,
    }


def build_targeting_dataset(latest: pd.DataFrame, predictions: pd.DataFrame) -> pd.DataFrame:
    with connect() as conn:
        user_context = pd.read_sql_query(
            """SELECT m.user_id, m.acquisition_channel, m.successful_transaction_count,
                      m.successful_transaction_volume, m.target_rate_user_flag, m.rate_alert_user_flag
               FROM mart_user_lifecycle m""",
            conn,
        )
    targeting = latest.merge(predictions, on=["user_id", "observation_date", "target_repeat_30d"])
    targeting = targeting.merge(user_context, on="user_id", how="left")
    targeting["probability_segment"] = pd.cut(
        targeting["repeat_probability"],
        bins=[-0.01, 0.35, 0.7, 1.0],
        labels=["Low repeat probability", "Medium repeat probability", "High repeat probability"],
    ).astype(str)
    positive_volume = targeting.loc[targeting["total_volume_90d"] > 0, "total_volume_90d"]
    high_value_cutoff = positive_volume.quantile(0.75)
    targeting["value_segment"] = np.where(targeting["total_volume_90d"] >= high_value_cutoff, "High value", "Standard value")
    conditions = [
        (targeting["value_segment"] == "High value") & (targeting["repeat_probability"] < 0.5),
        targeting["transactions_90d"].eq(0),
        targeting["failed_ratio_90d"].ge(0.2),
        targeting["repeat_probability"].lt(0.35),
    ]
    targeting["risk_segment"] = np.select(
        conditions,
        ["High-value at-risk users", "No recent transaction users", "High failed transaction users", "Low repeat probability users"],
        default=targeting["probability_segment"] + " users",
    )
    targeting["recommended_action"] = np.select(
        conditions,
        ["Prioritize service recovery", "Send reactivation education", "Resolve transaction friction", "Test feature onboarding prompt"],
        default="Maintain engagement",
    )
    targeting["recommendation_reason"] = np.select(
        conditions,
        [
            "High recent value but below-median repeat likelihood.",
            "No transaction in the 90-day observation window.",
            "At least 20% of recent attempts failed.",
            "Low predicted repeat likelihood and suitable for a controlled test.",
        ],
        default="No immediate risk rule was triggered.",
    )
    targeting["estimated_fee_proxy_90d"] = targeting["total_volume_90d"] * 0.00025
    ordered = [
        "user_id", "observation_date", "target_repeat_30d", "repeat_probability",
        "predicted_repeat_30d", "probability_segment", "risk_segment",
        "recommended_action", "recommendation_reason", "recency_days",
        "transactions_90d", "transactions_all", "total_volume_90d",
        "estimated_fee_proxy_90d", "failed_ratio_90d", "value_segment",
        "acquisition_channel", "successful_transaction_count",
        "successful_transaction_volume", "target_rate_user_flag", "rate_alert_user_flag",
    ]
    return export_frame(targeting[ordered].sort_values("repeat_probability"), "user_repeat_targeting_dataset.csv")


def _normal_cdf(value: float) -> float:
    return 0.5 * (1 + math.erf(value / math.sqrt(2)))


def _two_proportion_result(control: pd.Series, treatment: pd.Series) -> dict:
    n0, n1 = len(control), len(treatment)
    p0, p1 = control.mean(), treatment.mean()
    pooled = (control.sum() + treatment.sum()) / (n0 + n1)
    pooled_se = math.sqrt(max(pooled * (1 - pooled) * (1 / n0 + 1 / n1), 1e-12))
    z = (p1 - p0) / pooled_se
    p_value = 2 * (1 - _normal_cdf(abs(z)))
    diff_se = math.sqrt(max(p0 * (1 - p0) / n0 + p1 * (1 - p1) / n1, 1e-12))
    uplift = p1 - p0
    return {
        "control_n": n0,
        "treatment_n": n1,
        "control_rate": p0,
        "treatment_rate": p1,
        "absolute_uplift": uplift,
        "relative_uplift": uplift / p0 if p0 else np.nan,
        "ci_95_low": uplift - 1.96 * diff_se,
        "ci_95_high": uplift + 1.96 * diff_se,
        "z_statistic": z,
        "p_value": p_value,
        "statistically_significant_5pct": p_value < 0.05,
    }


def run_simulated_ab_test() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    design = pd.DataFrame(
        [
            {"field": "data_source", "definition": "Simulated randomized assignment and outcomes; demonstration only, not production causal evidence."},
            {"field": "unit_of_randomization", "definition": "User"},
            {"field": "control", "definition": "Existing onboarding with no feature prompt"},
            {"field": "treatment", "definition": "Onboarding prompt introducing rate-alert or target-rate order"},
            {"field": "primary_metric", "definition": "Feature adoption within 7 days"},
            {"field": "secondary_metric", "definition": "First exchange within 14 days"},
            {"field": "guardrail_metric", "definition": "Failed transaction or support ticket within 30 days"},
            {"field": "minimum_practical_effect", "definition": "2 percentage-point absolute uplift in the primary metric"},
        ]
    )
    export_frame(design, "ab_test_design.csv")
    with connect() as conn:
        users = pd.read_sql_query(
            """SELECT user_id, acquisition_channel,
                      CASE WHEN successful_transaction_volume >= 10000000 THEN 'High value' ELSE 'Standard value' END value_segment
               FROM mart_user_lifecycle WHERE onboarding_valid_flag=1""",
            conn,
        )
    rng = np.random.default_rng(RANDOM_STATE)
    experiment = users.copy()
    experiment["variant"] = rng.choice(["control", "treatment"], len(experiment))
    channel_adjustment = experiment["acquisition_channel"].map(
        {"referral": 0.03, "direct": 0.02, "organic_search": 0.01, "paid_social": -0.01}
    ).fillna(0)
    treatment = experiment["variant"].eq("treatment").astype(float)
    experiment["feature_adoption_7d"] = rng.binomial(1, np.clip(0.21 + channel_adjustment + 0.045 * treatment, 0.02, 0.95))
    experiment["first_exchange_14d"] = rng.binomial(1, np.clip(0.20 + channel_adjustment + 0.018 * treatment, 0.02, 0.95))
    experiment["guardrail_event_30d"] = rng.binomial(1, np.clip(0.075 - 0.004 * treatment, 0.01, 0.4))

    metric_map = {
        "feature_adoption_7d": "primary",
        "first_exchange_14d": "secondary",
        "guardrail_event_30d": "guardrail",
    }
    result_rows = []
    for metric, role in metric_map.items():
        result = _two_proportion_result(
            experiment.loc[experiment["variant"] == "control", metric],
            experiment.loc[experiment["variant"] == "treatment", metric],
        )
        result_rows.append(
            {
                "metric": metric,
                "metric_role": role,
                **result,
                "practically_significant": abs(result["absolute_uplift"]) >= (0.02 if role == "primary" else 0.01),
                "data_source": "simulated",
            }
        )
    results = export_frame(pd.DataFrame(result_rows), "ab_test_results.csv")

    segment_rows = []
    for segment_type in ["acquisition_channel", "value_segment"]:
        for segment, group in experiment.groupby(segment_type):
            if group["variant"].value_counts().min() < 100:
                continue
            result = _two_proportion_result(
                group.loc[group["variant"] == "control", "feature_adoption_7d"],
                group.loc[group["variant"] == "treatment", "feature_adoption_7d"],
            )
            segment_rows.append(
                {
                    "segment_type": segment_type,
                    "segment": segment,
                    "metric": "feature_adoption_7d",
                    **result,
                    "data_source": "simulated",
                }
            )
    segments = export_frame(pd.DataFrame(segment_rows), "ab_test_segment_results.csv")
    return design, results, segments


def run_campaign_simulator(targeting: pd.DataFrame | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    if targeting is None:
        targeting = pd.read_csv(CSV_DIR / "user_repeat_targeting_dataset.csv")
    audience = targeting[targeting["risk_segment"] != "High repeat probability users"].copy()
    baseline_repeat_users = audience["repeat_probability"].sum()
    average_volume = audience.loc[audience["total_volume_90d"] > 0, "total_volume_90d"].median()
    uplift_assumptions = {"low": 0.02, "base": 0.05, "high": 0.08}
    fee_assumptions = {"low": 0.00015, "base": 0.00025, "high": 0.00035}
    rows = []
    for uplift_label, uplift in uplift_assumptions.items():
        incremental_users = len(audience) * uplift
        for fee_label, fee_proxy in fee_assumptions.items():
            incremental_volume = incremental_users * average_volume
            rows.append(
                {
                    "audience_users": len(audience),
                    "baseline_expected_repeat_users": baseline_repeat_users,
                    "uplift_scenario": uplift_label,
                    "absolute_uplift_assumption": uplift,
                    "incremental_repeat_users": incremental_users,
                    "median_recent_volume_proxy_krw": average_volume,
                    "incremental_volume_proxy_krw": incremental_volume,
                    "fee_proxy_scenario": fee_label,
                    "fee_proxy_rate_assumption": fee_proxy,
                    "value_impact_proxy_krw": incremental_volume * fee_proxy,
                    "assumption_note": "Directional scenario only; not forecast revenue or causal impact.",
                }
            )
    sensitivity = pd.DataFrame(rows)
    base = sensitivity[
        (sensitivity["uplift_scenario"] == "base") & (sensitivity["fee_proxy_scenario"] == "base")
    ].copy()
    return export_frame(base, "campaign_simulator_outputs.csv"), export_frame(sensitivity, "campaign_sensitivity_analysis.csv")


def run_fx_readiness_model(refresh_market_data: bool = False) -> dict[str, pd.DataFrame]:
    """Build an operational volatility signal from cached Yahoo Finance market data."""
    from sklearn.metrics import balanced_accuracy_score

    prices, source_metadata = load_yahoo_fx_prices(refresh=refresh_market_data)
    available_pairs = [
        label for label in YAHOO_FX_TICKERS if f"{label}_close" in prices.columns
    ]
    features_frame = prices.copy()
    for pair in available_pairs:
        close = features_frame[f"{pair}_close"]
        features_frame[f"{pair}_return_1d"] = close.pct_change(fill_method=None)
        features_frame[f"{pair}_log_return_1d"] = np.log(close).diff()
        for window in [5, 10, 20]:
            features_frame[f"{pair}_vol_{window}d"] = (
                features_frame[f"{pair}_log_return_1d"].rolling(window).std() * np.sqrt(252)
            )
            features_frame[f"{pair}_momentum_{window}d"] = close / close.shift(window) - 1
        features_frame[f"{pair}_ma_gap_5_20"] = (
            close.rolling(5).mean() / close.rolling(20).mean() - 1
        )

    features_frame["USDKRW_intraday_range_pct"] = (
        features_frame["USDKRW_high"] - features_frame["USDKRW_low"]
    ) / features_frame["USDKRW_close"]
    features_frame["target_next_abs_return"] = (
        features_frame["USDKRW_log_return_1d"].abs().shift(-1)
    )
    features = [
        column
        for column in features_frame.columns
        if any(
            token in column
            for token in ["return_1d", "vol_", "momentum_", "ma_gap", "intraday_range"]
        )
    ]
    data = features_frame[features + ["target_next_abs_return"]].dropna().copy()
    split = int(len(data) * 0.8)
    base_train, base_test = data.iloc[:split].copy(), data.iloc[split:].copy()

    class_order = ["low", "normal", "high"]
    low, high = base_train["target_next_abs_return"].quantile([0.33, 0.67])
    quantile_label = lambda values: pd.cut(
        values,
        [-np.inf, low, high, np.inf],
        labels=class_order,
    ).astype(str)
    definitions = {
        "Quantile tercile": {
            "y_train": quantile_label(base_train["target_next_abs_return"]),
            "y_test": quantile_label(base_test["target_next_abs_return"]),
            "method": "train_quantile",
            "low_threshold": float(low),
            "high_threshold": float(high),
            "cluster_centers": None,
            "cluster_to_regime": None,
        }
    }

    kmeans = KMeans(n_clusters=3, random_state=RANDOM_STATE, n_init=20)
    kmeans.fit(base_train[["target_next_abs_return"]])
    centers = kmeans.cluster_centers_.ravel()
    center_order = np.argsort(centers)
    cluster_to_regime = {
        int(cluster_id): class_order[position]
        for position, cluster_id in enumerate(center_order)
    }
    definitions["KMeans volatility clusters"] = {
        "y_train": pd.Series(
            [cluster_to_regime[int(value)] for value in kmeans.predict(base_train[["target_next_abs_return"]])],
            index=base_train.index,
        ),
        "y_test": pd.Series(
            [cluster_to_regime[int(value)] for value in kmeans.predict(base_test[["target_next_abs_return"]])],
            index=base_test.index,
        ),
        "method": "train_kmeans_1d_abs_return",
        "low_threshold": None,
        "high_threshold": None,
        "cluster_centers": [float(value) for value in centers],
        "cluster_to_regime": cluster_to_regime,
    }

    model_specs = {
        "Logistic Regression": lambda: Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                ("scale", StandardScaler()),
                (
                    "model",
                    LogisticRegression(
                        max_iter=1500,
                        class_weight="balanced",
                        random_state=RANDOM_STATE,
                    ),
                ),
            ]
        ),
        "Random Forest": lambda: RandomForestClassifier(
            n_estimators=250,
            max_depth=8,
            min_samples_leaf=20,
            class_weight="balanced_subsample",
            n_jobs=-1,
            random_state=RANDOM_STATE,
        ),
    }
    metric_rows = []
    fitted = {}
    for definition_name, definition in definitions.items():
        for model_name, factory in model_specs.items():
            model = factory()
            model.fit(base_train[features], definition["y_train"])
            predicted = model.predict(base_test[features])
            metric_rows.append(
                {
                    "regime_definition": definition_name,
                    "model": model_name,
                    "accuracy": accuracy_score(definition["y_test"], predicted),
                    "balanced_accuracy": balanced_accuracy_score(definition["y_test"], predicted),
                    "precision_macro": precision_score(
                        definition["y_test"], predicted, average="macro", zero_division=0
                    ),
                    "recall_macro": recall_score(
                        definition["y_test"], predicted, average="macro", zero_division=0
                    ),
                    "f1_macro": f1_score(
                        definition["y_test"], predicted, average="macro", zero_division=0
                    ),
                }
            )
            fitted[(definition_name, model_name)] = model

    metrics = pd.DataFrame(metric_rows).sort_values(
        ["f1_macro", "balanced_accuracy"], ascending=False
    )
    best = metrics.iloc[0]
    selected_definition = best["regime_definition"]
    selected_model_name = best["model"]
    metrics["selected_model_flag"] = (
        metrics["regime_definition"].eq(selected_definition)
        & metrics["model"].eq(selected_model_name)
    ).astype(int)
    export_frame(metrics, "fx_volatility_model_metrics.csv")

    model = fitted[(selected_definition, selected_model_name)]
    y_test = definitions[selected_definition]["y_test"]
    predicted = model.predict(base_test[features])
    probabilities = model.predict_proba(base_test[features])
    predictions = pd.DataFrame(
        {
            "date": base_test.index.date,
            "actual_regime": y_test.values,
            "predicted_regime": predicted,
        }
    )
    for class_index, class_name in enumerate(model.classes_):
        predictions[f"prob_{class_name}"] = probabilities[:, class_index]
    action = {
        "low": "Normal monitoring; use calmer periods for product education.",
        "normal": "Maintain standard staffing and transaction monitoring.",
        "high": "Prepare support coverage, rate-change messaging, and tighter transaction monitoring.",
    }
    predictions["recommended_action"] = predictions["predicted_regime"].map(action)
    export_frame(predictions, "fx_volatility_predictions.csv")

    matrix = pd.DataFrame(
        confusion_matrix(y_test, predicted, labels=class_order),
        index=[f"Actual {label}" for label in class_order],
        columns=[f"Predicted {label}" for label in class_order],
    )
    matrix.index.name = "actual_regime"
    export_frame(matrix.reset_index(), "fx_volatility_confusion_matrix.csv")
    estimator = model.named_steps["model"] if isinstance(model, Pipeline) else model
    values = (
        estimator.feature_importances_
        if hasattr(estimator, "feature_importances_")
        else np.abs(estimator.coef_).mean(axis=0)
    )
    importance = pd.DataFrame(
        {"feature": features, "importance": values}
    ).sort_values("importance", ascending=False)
    export_frame(importance, "fx_volatility_feature_importance.csv")
    export_frame(data.reset_index(), "fx_market_features.csv")

    metadata_rows = []
    for name, definition in definitions.items():
        metadata_rows.append(
            {
                "regime_definition": name,
                "method": definition["method"],
                "low_threshold": definition["low_threshold"],
                "high_threshold": definition["high_threshold"],
                "cluster_centers": (
                    None
                    if definition["cluster_centers"] is None
                    else ", ".join(f"{value:.8f}" for value in definition["cluster_centers"])
                ),
                "cluster_to_regime": (
                    None
                    if definition["cluster_to_regime"] is None
                    else str(definition["cluster_to_regime"])
                ),
                "train_end": base_train.index.max().date().isoformat(),
                "test_start": base_test.index.min().date().isoformat(),
                "data_provider": "Yahoo Finance",
            }
        )
    export_frame(pd.DataFrame(metadata_rows), "fx_volatility_regime_metadata.csv")

    best_by_definition = (
        metrics.sort_values(
            ["regime_definition", "f1_macro", "balanced_accuracy"],
            ascending=[True, False, False],
        )
        .drop_duplicates("regime_definition")
        .rename(columns={"model": "best_model_by_f1", "f1_macro": "best_f1_macro"})
    )
    comparison = best_by_definition[
        ["regime_definition", "best_model_by_f1", "best_f1_macro", "balanced_accuracy"]
    ].rename(columns={"balanced_accuracy": "balanced_accuracy_for_best_f1_model"})
    export_frame(comparison, "fx_volatility_regime_definition_comparison.csv")

    source_export = pd.DataFrame(
        [
            {
                "provider": source_metadata["provider"],
                "library": source_metadata["library"],
                "tickers": ", ".join(
                    f"{label}:{ticker}" for label, ticker in source_metadata["tickers"].items()
                ),
                "first_observation": source_metadata["first_observation"],
                "last_observation": source_metadata["last_observation"],
                "rows": source_metadata["rows"],
                "cache_path": source_metadata["cache_path"],
                "load_mode": source_metadata["load_mode"],
                "data_classification": source_metadata["data_classification"],
            }
        ]
    )
    export_frame(source_export, "fx_data_source.csv")
    with (MODEL_DIR / "fx_volatility_regime_model.pkl").open("wb") as file:
        pickle.dump(
            {
                "model": model,
                "model_name": selected_model_name,
                "features": features,
                "class_order": class_order,
                "regime_definition": selected_definition,
                "regime_metadata": definitions[selected_definition],
                "available_pairs": available_pairs,
                "data_source": source_metadata,
            },
            file,
        )
    return {
        "metrics": metrics,
        "predictions": predictions,
        "importance": importance,
        "source": source_export,
    }


def run_all() -> dict[str, object]:
    project_setup()
    build_data_mart()
    overview = dataset_overview()
    quality = run_data_quality_checks()
    product = export_product_analysis()
    repeat = train_repeat_models()
    experiment = run_simulated_ab_test()
    campaign = run_campaign_simulator(repeat["targeting"])
    fx = run_fx_readiness_model()
    return {
        "overview": overview,
        "quality": quality,
        "product": product,
        "repeat": repeat,
        "experiment": experiment,
        "campaign": campaign,
        "fx": fx,
    }
