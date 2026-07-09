import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard.charts import cohort_heatmap, funnel_chart, horizontal_bar
from dashboard.config import PAGES
from dashboard.data_loader import load_data
from dashboard.ui import page_intro, pattern, percent


st.set_page_config(page_title="FX Fintech Product Analytics", layout="wide")
data = load_data()
page = st.sidebar.radio("Page", PAGES)
st.sidebar.caption("Synthetic product behavior; Yahoo Finance FX market data.")


if page == "Executive Summary":
    page_intro(
        page,
        "14-day activation, D30 repeat, feature adoption, and targetable users",
        "Prioritize onboarding friction and test feature prompts with a randomized experiment.",
        "The source data is synthetic; descriptive relationships are not causal.",
    )
    funnel = data["funnel"].iloc[0]
    repeat = data["repeat_channel"]
    feature = data["feature"]
    targeting = data["targeting"]
    cols = st.columns(4)
    cols[0].metric("Valid signups", f"{funnel['valid_signups']:,.0f}")
    cols[1].metric("14-day activation", percent(100 * funnel["activated_within_14_days"] / funnel["valid_signups"]))
    cols[2].metric("D30 repeat", percent(repeat["d30_repeat_users"].sum() / repeat["first_exchange_users"].sum() * 100))
    cols[3].metric("Priority audience", f"{(targeting['risk_segment'] != 'High repeat probability users').sum():,.0f}")
    pattern("The largest funnel loss occurs before first exchange; channel quality differs more on activation than signup volume.")
    st.plotly_chart(funnel_chart(data["funnel"]), width="stretch")


elif page == "Funnel and Retention":
    page_intro(
        page,
        "Stage conversion, 14-day activation, and monthly post-exchange retention",
        "Diagnose the weakest onboarding step by channel and set lifecycle messaging around early repeat windows.",
        "Later cohorts have incomplete retention windows and should not be compared at unavailable tenures.",
    )
    left, right = st.columns(2)
    left.plotly_chart(funnel_chart(data["funnel"]), width="stretch")
    channel = data["channel"].merge(data["repeat_channel"], on="acquisition_channel", how="left")
    right.plotly_chart(
        horizontal_bar(channel, "activation_rate_14d", "acquisition_channel", "14-day activation %"),
        width="stretch",
    )
    pattern("Referral and direct acquisition can be evaluated on both activation and D30 repeat, not volume alone.")
    st.plotly_chart(cohort_heatmap(data["cohort"]), width="stretch")


elif page == "Feature Adoption and Simulated A/B Test":
    page_intro(
        page,
        "Feature adoption within 7 days and repeat-rate association",
        "Use the onboarding prompt experiment to test adoption lift; treat observational retention gaps as hypotheses.",
        "Simulated experiment analysis to demonstrate A/B testing logic; assignment and outcomes are not production causal evidence.",
    )
    st.warning(
        "The experiment table below contains generated assignment and outcomes. "
        "It demonstrates the evaluation method and does not estimate real product uplift."
    )
    left, right = st.columns(2)
    left.plotly_chart(
        px.bar(data["feature"], x="feature", y="adoption_rate", text_auto=".1f", labels={"adoption_rate": "Adoption %"}),
        width="stretch",
    )
    feature_retention = data["feature_retention"]
    right.plotly_chart(
        px.bar(feature_retention, x="user_group", y="d30_repeat_rate", color="comparison_type", barmode="group", labels={"d30_repeat_rate": "D30 repeat %"}),
        width="stretch",
    )
    result = data["ab_results"]
    display = result[["metric", "control_rate", "treatment_rate", "absolute_uplift", "ci_95_low", "ci_95_high", "p_value", "practically_significant"]].copy()
    for column in ["control_rate", "treatment_rate", "absolute_uplift", "ci_95_low", "ci_95_high"]:
        display[column] = (display[column] * 100).round(2)
    pattern("Statistical significance and the minimum practical effect are reported separately.")
    st.dataframe(display, width="stretch", hide_index=True)


elif page == "Prediction and Targeting":
    page_intro(
        page,
        "Next-30-day repeat probability from a trailing 90-day observation window",
        "Use scores to prioritize controlled CRM tests and service recovery, not automatic exclusion.",
        "Validation is time-based but still uses synthetic behavior; scores require calibration and drift checks before deployment.",
    )
    metrics = data["model_metrics"]
    st.dataframe(
        metrics[["model", "roc_auc", "pr_auc", "precision", "recall", "f1", "selected_model_flag"]],
        width="stretch",
        hide_index=True,
    )
    left, right = st.columns(2)
    left.plotly_chart(
        horizontal_bar(data["importance"], "importance", "feature", "Model importance"),
        width="stretch",
    )
    segments = data["targeting"].groupby("risk_segment", as_index=False).agg(
        users=("user_id", "count"), avg_repeat_probability=("repeat_probability", "mean")
    )
    right.plotly_chart(horizontal_bar(segments, "users", "risk_segment", "Users"), width="stretch")
    pattern("Targeting rules combine probability with recent inactivity, value, and failed-transaction context.")
    scenario = data["campaign"]
    st.dataframe(
        scenario[["uplift_scenario", "fee_proxy_scenario", "absolute_uplift_assumption", "incremental_repeat_users", "value_impact_proxy_krw", "assumption_note"]],
        width="stretch",
        hide_index=True,
    )


elif page == "FX Market Readiness":
    page_intro(
        page,
        "Next-day volatility regime classification and transaction success by historical regime",
        "Use high-volatility signals for staffing, monitoring, rate-change messaging, and campaign timing.",
        "Yahoo Finance market data is real historical data; product outcomes are synthetic and the signal is not a trading forecast.",
    )
    source = data["fx_source"].iloc[0]
    st.caption(
        f"Market source: {source['provider']} | {source['first_observation']} to "
        f"{source['last_observation']} | {source['tickers']}"
    )
    st.dataframe(data["fx_metrics"], width="stretch", hide_index=True)
    left, right = st.columns(2)
    left.plotly_chart(
        px.bar(
            data["fx_behavior"],
            x="market_regime_at_transaction",
            y="success_rate",
            labels={"success_rate": "Transaction success %"},
            title="Synthetic transactions by simulated regime",
        ),
        width="stretch",
    )
    predictions = data["fx_predictions"].tail(120).copy()
    right.plotly_chart(
        px.scatter(
            predictions,
            x="date",
            y="predicted_regime",
            color="predicted_regime",
            category_orders={"predicted_regime": ["low", "normal", "high"]},
            title="Yahoo Finance out-of-time regime predictions",
        ),
        width="stretch",
    )
    pattern("Readiness recommendations are tied to predicted regime and should be validated against operational outcomes.")


else:
    page_intro(
        page,
        "Validity, completeness, duplicate, leakage, and modeling-window checks",
        "Resolve error-level issues before metric release; document warnings and review-only outliers.",
        "Missingness can be expected for conditionally optional fields and is not automatically a data defect.",
    )
    st.dataframe(data["quality_summary"], width="stretch", hide_index=True)
    issues = data["quality_issues"]
    st.dataframe(issues[issues["issue_count"] > 0], width="stretch", hide_index=True)
    pattern("Duplicate event keys are removed in the clean event view; transaction outliers are flagged but retained.")
    st.markdown(
        """
        **Methodology**

        - Activation: KYC, bank link, and first successful exchange within 14 days of signup.
        - D30 repeat: another successful exchange within 30 days of first exchange.
        - Repeat model: trailing 90-day features, chronological validation, following 30-day target.
        - A/B test: simulated demonstration with user-level randomization.
        - FX signal: lagged USD/KRW features with a chronological split.
        """
    )
