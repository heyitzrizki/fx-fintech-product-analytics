import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from dashboard.config import COLORS


px.defaults.template = "plotly_white"


def funnel_chart(funnel: pd.DataFrame):
    row = funnel.iloc[0]
    labels = ["Valid signup", "KYC completed", "Bank linked", "First exchange", "Activated in 14 days"]
    values = [
        row["valid_signups"], row["kyc_completed"], row["bank_linked"],
        row["first_successful_exchange"], row["activated_within_14_days"],
    ]
    return go.Figure(go.Funnel(y=labels, x=values, marker={"color": COLORS["teal"]})).update_layout(height=380)


def cohort_heatmap(cohort: pd.DataFrame):
    recent = cohort[cohort["months_since_first_transaction"].between(1, 6)].copy()
    pivot = recent.pivot(index="cohort_month", columns="months_since_first_transaction", values="retention_rate").tail(12)
    return px.imshow(
        pivot,
        text_auto=".1f",
        aspect="auto",
        color_continuous_scale="Blues",
        labels={"color": "Retention %", "x": "Months since first exchange", "y": "Cohort"},
    ).update_layout(height=430)


def horizontal_bar(frame: pd.DataFrame, x: str, y: str, label: str):
    ordered = frame.sort_values(x)
    return px.bar(ordered, x=x, y=y, orientation="h", color_discrete_sequence=[COLORS["navy"]], labels={x: label}).update_layout(height=380)
