from pathlib import Path
import argparse

import matplotlib
import pandas as pd


matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CSV_DIR = PROJECT_ROOT / "outputs" / "csv"
FIGURE_DIR = PROJECT_ROOT / "outputs" / "figures"

FIGURE_DPI = 160

COLOR_TEAL = "#2f6f73"
COLOR_NAVY = "#2f4b7c"
COLOR_GREEN = "#6b8e23"
COLOR_COPPER = "#8f5b2e"
COLOR_PLUM = "#7b6d8d"
COLOR_ROSE = "#b279a2"
COLOR_GRAY = "#6f6f6f"


def read_csv(file_name: str) -> pd.DataFrame:
    csv_path = CSV_DIR / file_name

    if not csv_path.exists():
        raise FileNotFoundError(f"Missing CSV file: {csv_path}")

    return pd.read_csv(csv_path)


def save_figure(fig: plt.Figure, file_name: str, overwrite: bool = False) -> None:
    output_path = FIGURE_DIR / file_name

    if output_path.exists() and not overwrite:
        print(f"SKIP existing figure: {output_path}")
        plt.close(fig)
        return

    fig.tight_layout()
    fig.savefig(output_path, dpi=FIGURE_DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"EXPORTED {output_path.name}")


def add_bar_labels(ax: plt.Axes, labels_are_percent: bool = False) -> None:
    for container in ax.containers:
        labels = []
        for value in container.datavalues:
            if labels_are_percent:
                labels.append(f"{value:.1f}%")
            else:
                labels.append(f"{value:,.0f}")
        ax.bar_label(container, labels=labels, padding=3, fontsize=8)


def clean_label(value: str) -> str:
    return str(value).replace("_", " ").capitalize()


def create_product_funnel(overwrite: bool) -> None:
    df = read_csv("product_funnel.csv")
    signup_column = "valid_signups" if "valid_signups" in df.columns else "signups"

    funnel_steps = {
        "Valid signups": signup_column,
        "KYC completed": "kyc_completed",
        "Bank linked": "bank_linked",
        "First exchange": "first_successful_exchange",
        "Activated 14d": "activated_within_14_days",
    }

    values = [df.loc[0, column] for column in funnel_steps.values()]

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(funnel_steps.keys(), values, color=COLOR_TEAL)
    ax.set_title("Product Onboarding Funnel")
    ax.set_ylabel("Users")
    ax.tick_params(axis="x", rotation=20)
    ax.spines[["top", "right"]].set_visible(False)
    add_bar_labels(ax)

    save_figure(fig, "product_funnel.png", overwrite)


def create_activation_by_channel(overwrite: bool) -> None:
    df = read_csv("funnel_by_acquisition_channel.csv")
    df["channel_label"] = df["acquisition_channel"].map(clean_label)
    df = df.sort_values("activation_rate_14d", ascending=True)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(df["channel_label"], df["activation_rate_14d"], color=COLOR_GREEN)
    ax.set_title("14-Day Activation Rate by Acquisition Channel")
    ax.set_xlabel("Activation rate")
    ax.spines[["top", "right"]].set_visible(False)
    ax.xaxis.set_major_formatter(lambda value, _: f"{value:.0f}%")
    add_bar_labels(ax, labels_are_percent=True)

    save_figure(fig, "activation_rate_by_channel.png", overwrite)


def create_d30_repeat_by_channel(overwrite: bool) -> None:
    df = read_csv("d30_repeat_by_channel.csv")
    df["channel_label"] = df["acquisition_channel"].map(clean_label)
    df = df.sort_values("d30_repeat_rate", ascending=True)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(df["channel_label"], df["d30_repeat_rate"], color=COLOR_COPPER)
    ax.set_title("D30 Repeat Rate by Acquisition Channel")
    ax.set_xlabel("D30 repeat rate")
    ax.spines[["top", "right"]].set_visible(False)
    ax.xaxis.set_major_formatter(lambda value, _: f"{value:.0f}%")
    add_bar_labels(ax, labels_are_percent=True)

    save_figure(fig, "d30_repeat_by_channel.png", overwrite)


def create_feature_combination_retention(overwrite: bool) -> None:
    df = read_csv("feature_combination_retention.csv")
    df = df.sort_values("d30_repeat_rate", ascending=True)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(df["feature_group"], df["d30_repeat_rate"], color=COLOR_NAVY)
    ax.set_title("D30 Repeat Rate by Feature Adoption")
    ax.set_xlabel("D30 repeat rate")
    ax.spines[["top", "right"]].set_visible(False)
    ax.xaxis.set_major_formatter(lambda value, _: f"{value:.0f}%")
    add_bar_labels(ax, labels_are_percent=True)

    save_figure(fig, "feature_combination_retention.png", overwrite)


def create_fx_regime_success_rate(overwrite: bool) -> None:
    df = read_csv("fx_regime_behavior.csv")
    regime_order = ["low", "normal", "high"]
    df["market_regime_at_transaction"] = pd.Categorical(
        df["market_regime_at_transaction"],
        categories=regime_order,
        ordered=True,
    )
    df = df.sort_values("market_regime_at_transaction")

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(
        df["market_regime_at_transaction"].astype(str),
        df["success_rate"],
        color=COLOR_PLUM,
    )
    ax.set_title("Exchange Success Rate by FX Volatility Regime")
    ax.set_xlabel("FX regime")
    ax.set_ylabel("Success rate")
    ax.set_ylim(0, 100)
    ax.spines[["top", "right"]].set_visible(False)
    ax.yaxis.set_major_formatter(lambda value, _: f"{value:.0f}%")
    add_bar_labels(ax, labels_are_percent=True)

    save_figure(fig, "fx_regime_success_rate.png", overwrite)


def create_fx_regime_activity_and_success(overwrite: bool) -> None:
    behavior = read_csv("fx_regime_behavior.csv")
    activity = read_csv("fx_regime_normalized_activity.csv")

    df = activity.merge(
        behavior[["market_regime_at_transaction", "success_rate"]],
        left_on="market_regime",
        right_on="market_regime_at_transaction",
        how="left",
    )

    regime_order = ["low", "normal", "high"]
    df["market_regime"] = pd.Categorical(
        df["market_regime"],
        categories=regime_order,
        ordered=True,
    )
    df = df.sort_values("market_regime")

    fig, ax1 = plt.subplots(figsize=(9, 5))
    ax2 = ax1.twinx()

    bars = ax1.bar(
        df["market_regime"].astype(str),
        df["attempts_per_regime_hour"],
        color=COLOR_TEAL,
        label="Attempts per regime hour",
    )
    line = ax2.plot(
        df["market_regime"].astype(str),
        df["success_rate"],
        color=COLOR_COPPER,
        marker="o",
        linewidth=2,
        label="Success rate",
    )

    ax1.set_title("FX Regime Activity and Exchange Success", pad=30)
    ax1.set_xlabel("FX regime")
    ax1.set_ylabel("Attempts per regime hour")
    ax2.set_ylabel("Success rate")
    ax2.yaxis.set_major_formatter(lambda value, _: f"{value:.0f}%")
    ax2.set_ylim(85, 95)
    ax1.spines["top"].set_visible(False)
    ax2.spines["top"].set_visible(False)
    ax1.bar_label(bars, labels=[f"{value:.2f}" for value in df["attempts_per_regime_hour"]], padding=3, fontsize=8)

    handles = [bars, line[0]]
    labels = [handle.get_label() for handle in handles]
    ax1.legend(
        handles,
        labels,
        frameon=False,
        loc="lower center",
        bbox_to_anchor=(0.5, 1.01),
        ncol=2,
    )

    save_figure(fig, "fx_regime_activity_and_success.png", overwrite)


def create_monthly_activation_trend(overwrite: bool) -> None:
    df = read_csv("monthly_product_trend.csv")
    df["signup_month"] = pd.to_datetime(df["signup_month"])
    df = df.sort_values("signup_month")

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(
        df["signup_month"],
        df["activation_rate_14d"],
        marker="o",
        color=COLOR_NAVY,
        linewidth=2,
    )
    ax.set_title("Monthly 14-Day Activation Rate")
    ax.set_xlabel("Signup month")
    ax.set_ylabel("Activation rate")
    ax.spines[["top", "right"]].set_visible(False)
    ax.yaxis.set_major_formatter(lambda value, _: f"{value:.0f}%")
    fig.autofmt_xdate(rotation=30)

    save_figure(fig, "monthly_activation_trend.png", overwrite)


def create_monthly_signups_and_activation(overwrite: bool) -> None:
    df = read_csv("monthly_product_trend.csv")
    df["signup_month"] = pd.to_datetime(df["signup_month"])
    df = df.sort_values("signup_month")

    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax2 = ax1.twinx()

    bars = ax1.bar(
        df["signup_month"],
        df["valid_signups"],
        color=COLOR_TEAL,
        alpha=0.85,
        width=20,
        label="Valid signups",
    )
    line = ax2.plot(
        df["signup_month"],
        df["activation_rate_14d"],
        marker="o",
        color=COLOR_COPPER,
        linewidth=2,
        label="14-day activation rate",
    )

    ax1.set_title("Monthly Signups and 14-Day Activation Rate")
    ax1.set_xlabel("Signup month")
    ax1.set_ylabel("Valid signups")
    ax2.set_ylabel("Activation rate")
    ax2.yaxis.set_major_formatter(lambda value, _: f"{value:.0f}%")
    ax1.spines["top"].set_visible(False)
    ax2.spines["top"].set_visible(False)
    fig.autofmt_xdate(rotation=30)

    handles = [bars, line[0]]
    labels = [handle.get_label() for handle in handles]
    ax1.legend(handles, labels, frameon=False, loc="upper left")

    save_figure(fig, "monthly_signups_and_activation.png", overwrite)


def create_cohort_retention_heatmap(overwrite: bool) -> None:
    df = read_csv("cohort_retention.csv")
    df["cohort_month"] = pd.to_datetime(df["cohort_month"]).dt.strftime("%Y-%m")

    pivot = df.pivot(
        index="cohort_month",
        columns="months_since_first_transaction",
        values="retention_rate",
    ).sort_index()

    fig, ax = plt.subplots(figsize=(9, 8))
    image = ax.imshow(pivot, aspect="auto", cmap="YlGnBu", vmin=0, vmax=100)

    ax.set_title("Cohort Retention Heatmap")
    ax.set_xlabel("Months since first transaction")
    ax.set_ylabel("First transaction cohort")
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)

    colorbar = fig.colorbar(image, ax=ax)
    colorbar.set_label("Retention rate")
    colorbar.ax.yaxis.set_major_formatter(lambda value, _: f"{value:.0f}%")

    save_figure(fig, "cohort_retention_heatmap.png", overwrite)


def create_cohort_retention_heatmap_excluding_m0(overwrite: bool) -> None:
    df = read_csv("cohort_retention.csv")
    df = df[df["months_since_first_transaction"] > 0].copy()
    df["cohort_month"] = pd.to_datetime(df["cohort_month"]).dt.strftime("%Y-%m")

    pivot = df.pivot(
        index="cohort_month",
        columns="months_since_first_transaction",
        values="retention_rate",
    ).sort_index()

    fig, ax = plt.subplots(figsize=(8, 8))
    image = ax.imshow(pivot, aspect="auto", cmap="YlGnBu", vmin=30, vmax=75)

    ax.set_title("Cohort Retention Heatmap Excluding M0")
    ax.set_xlabel("Months since first transaction")
    ax.set_ylabel("First transaction cohort")
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)

    colorbar = fig.colorbar(image, ax=ax)
    colorbar.set_label("Retention rate")
    colorbar.ax.yaxis.set_major_formatter(lambda value, _: f"{value:.0f}%")

    save_figure(fig, "cohort_retention_heatmap_excluding_m0.png", overwrite)


def create_support_ticket_impact(overwrite: bool) -> None:
    df = read_csv("support_ticket_impact.csv")

    group_order = [
        "No support ticket",
        "One support ticket",
        "Multiple support tickets",
    ]
    df["support_group"] = pd.Categorical(
        df["support_group"],
        categories=group_order,
        ordered=True,
    )
    df = df.sort_values("support_group")

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(df["support_group"].astype(str), df["d30_repeat_rate"], color=COLOR_ROSE)
    ax.set_title("D30 Repeat Rate by Support Ticket Exposure")
    ax.set_ylabel("D30 repeat rate")
    ax.tick_params(axis="x", rotation=15)
    ax.spines[["top", "right"]].set_visible(False)
    ax.yaxis.set_major_formatter(lambda value, _: f"{value:.0f}%")
    add_bar_labels(ax, labels_are_percent=True)

    save_figure(fig, "support_ticket_impact.png", overwrite)


def create_customer_value_feature_adoption(overwrite: bool) -> None:
    df = read_csv("customer_value_segmentation.csv")
    df["value_segment_label"] = df["value_segment"].replace(
        {
            "Q1 lowest volume": "Q1\nlowest volume",
            "Q4 highest volume": "Q4\nhighest volume",
        }
    )

    x = range(len(df))
    width = 0.38

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(
        [position - width / 2 for position in x],
        df["target_rate_adoption_rate"],
        width=width,
        label="Target-rate",
        color=COLOR_TEAL,
    )
    ax.bar(
        [position + width / 2 for position in x],
        df["rate_alert_adoption_rate"],
        width=width,
        label="Rate alert",
        color=COLOR_NAVY,
    )

    ax.set_title("Feature Adoption by Customer Value Segment")
    ax.set_ylabel("Adoption rate")
    ax.set_xticks(list(x))
    ax.set_xticklabels(df["value_segment_label"])
    ax.yaxis.set_major_formatter(lambda value, _: f"{value:.0f}%")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False)

    save_figure(fig, "customer_value_feature_adoption.png", overwrite)


def main(overwrite: bool = False) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    create_product_funnel(overwrite)
    create_activation_by_channel(overwrite)
    create_d30_repeat_by_channel(overwrite)
    create_feature_combination_retention(overwrite)
    create_fx_regime_success_rate(overwrite)
    create_fx_regime_activity_and_success(overwrite)
    create_monthly_activation_trend(overwrite)
    create_monthly_signups_and_activation(overwrite)
    create_cohort_retention_heatmap(overwrite)
    create_cohort_retention_heatmap_excluding_m0(overwrite)
    create_support_ticket_impact(overwrite)
    create_customer_value_feature_adoption(overwrite)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create portfolio figures from dashboard-ready CSV files."
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing figures in outputs/figures.",
    )

    args = parser.parse_args()
    main(overwrite=args.overwrite)
