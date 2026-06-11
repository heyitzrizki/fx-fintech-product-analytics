from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CSV_DIR = PROJECT_ROOT / "outputs" / "csv"

COLOR_TEXT = "#1F2937"
COLOR_MUTED = "#6B7280"
COLOR_BORDER = "#E5E7EB"
COLOR_PAGE = "#F7F9FC"
COLOR_CARD = "#FFFFFF"
COLOR_TEAL = "#2F6F73"
COLOR_NAVY = "#2F4B7C"
COLOR_BLUE = "#4C78A8"
COLOR_ORANGE = "#9C642C"
COLOR_PLUM = "#7B6D8D"
COLOR_ROSE = "#B279A2"

CHANNEL_LABELS = {
    "paid_social": "Paid social",
    "organic_search": "Organic search",
    "referral": "Referral",
    "direct": "Direct",
    "affiliate": "Affiliate",
    "content": "Content",
    "other": "Other",
}

CHANNEL_LABELS_KO = {
    "paid_social": "유료 소셜",
    "organic_search": "오가닉 검색",
    "referral": "추천",
    "direct": "직접 유입",
    "affiliate": "제휴",
    "content": "콘텐츠",
    "other": "기타",
}

LANGUAGE_OPTIONS = {
    "English": "en",
    "한국어": "ko",
}

TEXT = {
    "hero_title": {
        "en": "FX Fintech Product Analytics",
        "ko": "FX 핀테크 프로덕트 분석",
    },
    "hero_subtitle": {
        "en": "Synthetic product analytics case study using SQL marts, Python exports, and Streamlit.",
        "ko": "SQL 마트, Python 데이터 추출, Streamlit으로 구성한 합성 데이터 기반 프로덕트 분석 사례입니다.",
    },
    "synthetic_note": {
        "en": "Synthetic dataset for portfolio demonstration; not actual company performance.",
        "ko": "포트폴리오 시연을 위한 합성 데이터이며, 실제 회사 성과가 아닙니다.",
    },
    "valid_users": {"en": "Valid users", "ko": "유효 사용자"},
    "activation_14d": {"en": "14-day activation", "ko": "14일 활성화율"},
    "first_exchanges": {"en": "First exchanges", "ko": "첫 환전 완료 사용자"},
    "target_rate_users": {"en": "Target-rate users", "ko": "목표 환율 기능 사용자"},
    "rate_alert_users": {"en": "Rate-alert users (valid users)", "ko": "환율 알림 사용자 (유효 사용자)"},
    "valid_users_help": {
        "en": "Users included after onboarding quality filters.",
        "ko": "온보딩 품질 필터를 통과한 사용자입니다.",
    },
    "activation_help": {
        "en": "Completed KYC, linked bank, and first exchange within 14 days.",
        "ko": "가입 후 14일 이내 KYC, 계좌 연결, 첫 환전을 완료한 비율입니다.",
    },
    "first_exchange_help": {
        "en": "Users reaching first successful exchange.",
        "ko": "첫 번째 성공 환전에 도달한 사용자 수입니다.",
    },
    "target_rate_help": {
        "en": "Valid users with target-rate usage.",
        "ko": "목표 환율 주문 기능을 사용한 유효 사용자 수입니다.",
    },
    "rate_alert_help": {
        "en": "Rate-alert count is lifecycle-wide, not only first-exchange users.",
        "ko": "첫 환전 사용자만이 아니라 전체 유효 사용자 기준의 환율 알림 사용자 수입니다.",
    },
    "tab_overview": {"en": "Executive Overview", "ko": "핵심 요약"},
    "tab_acquisition": {"en": "Acquisition Quality", "ko": "유입 채널 품질"},
    "tab_retention": {"en": "Retention & Feature Adoption", "ko": "리텐션 및 기능 사용"},
    "tab_fx": {"en": "FX Regime & Transaction Reliability", "ko": "환율 변동성과 거래 안정성"},
    "tab_value": {"en": "Customer Value & Support", "ko": "고객 가치 및 고객지원"},
    "tab_method": {"en": "Data & Methodology", "ko": "데이터 및 방법론"},
    "overview_subtitle": {
        "en": "Business question: where does growth convert into durable product usage?",
        "ko": "비즈니스 질문: 성장한 가입자가 실제 지속 사용으로 전환되는 지점은 어디인가?",
    },
    "overview_finding_title": {"en": "Growth quality improved over time", "ko": "성장 품질이 시간이 지날수록 개선됨"},
    "overview_finding_text": {
        "en": "Recent signup cohorts expanded while 14-day activation also rose, suggesting healthier growth quality.",
        "ko": "최근 가입 코호트는 규모가 커지는 동시에 14일 활성화율도 상승해, 더 건강한 성장 흐름을 보입니다.",
    },
    "overview_funnel_title": {"en": "Fast activation remains the bottleneck", "ko": "빠른 활성화가 여전히 핵심 병목"},
    "overview_funnel_text": {
        "en": "The largest drop-off happens before users reach activated exchange behavior within the first 14 days.",
        "ko": "가장 큰 이탈은 사용자가 14일 이내 첫 환전 활성화에 도달하기 전에 발생합니다.",
    },
    "overview_retention_title": {"en": "Feature adoption is a strong signal", "ko": "기능 사용은 강한 리텐션 신호"},
    "overview_retention_text": {
        "en": "Target-rate and rate-alert adoption are strongly associated with higher D30 repeat behavior.",
        "ko": "목표 환율과 환율 알림 기능 사용자는 30일 반복 사용률이 더 높은 경향을 보입니다.",
    },
    "acquisition_subtitle": {
        "en": "Question: which channels bring users who activate and continue after first exchange?",
        "ko": "질문: 어떤 유입 채널이 빠르게 활성화되고 첫 환전 이후에도 반복 사용하는 사용자를 데려오는가?",
    },
    "acquisition_finding_title": {"en": "Referral leads activation quality", "ko": "추천 채널의 활성화 품질이 가장 높음"},
    "acquisition_finding_text": {
        "en": "Referral has the highest 14-day activation rate, while paid social delivers volume but weaker activation.",
        "ko": "추천 채널은 14일 활성화율이 가장 높고, 유료 소셜은 규모는 크지만 활성화 품질은 낮습니다.",
    },
    "repeat_finding_title": {"en": "Repeat rates converge after first exchange", "ko": "첫 환전 이후 반복률은 채널 간 차이가 작음"},
    "repeat_finding_text": {
        "en": "After users complete a first exchange, D30 repeat rates are tightly clustered across major channels.",
        "ko": "첫 환전을 완료한 이후에는 주요 채널 간 30일 반복률 차이가 크지 않습니다.",
    },
    "retention_subtitle": {
        "en": "Question: which product behaviors are associated with stronger repeat usage?",
        "ko": "질문: 어떤 제품 행동이 더 강한 반복 사용과 연결되는가?",
    },
    "feature_finding_title": {"en": "Both features together show the strongest repeat behavior", "ko": "두 기능을 함께 쓰는 사용자의 반복 사용이 가장 높음"},
    "feature_finding_text": {
        "en": "Users adopting both target-rate and rate-alert features have the highest D30 repeat rate.",
        "ko": "목표 환율과 환율 알림을 모두 사용하는 사용자가 가장 높은 30일 반복률을 보입니다.",
    },
    "feature_reco_title": {"en": "Help new users discover key features earlier", "ko": "신규 사용자가 핵심 기능을 더 빨리 발견하도록 유도"},
    "feature_reco_text": {
        "en": "Users who adopt both features repeat more often. The next business step is to test whether onboarding prompts can increase feature adoption and repeat usage.",
        "ko": "두 기능을 사용하는 사용자는 더 자주 반복 사용합니다. 다음 비즈니스 액션은 온보딩 안내가 기능 사용과 반복 사용을 높이는지 실험하는 것입니다.",
    },
    "fx_subtitle": {
        "en": "Question: how does market volatility affect transaction attempts and successful completion?",
        "ko": "질문: 환율 변동성은 거래 시도와 성공률에 어떤 영향을 주는가?",
    },
    "fx_finding_title": {"en": "High volatility increases activity but pressures reliability", "ko": "변동성이 높을수록 활동은 늘지만 거래 안정성은 낮아짐"},
    "fx_finding_text": {
        "en": "High-volatility regimes show slightly higher attempts per regime hour, but lower exchange success rate.",
        "ko": "고변동 구간에서는 시간당 거래 시도가 소폭 증가하지만, 환전 성공률은 낮아집니다.",
    },
    "failure_table": {"en": "Failure Reason by Regime", "ko": "변동성 구간별 실패 사유"},
    "value_subtitle": {
        "en": "Question: how do value segments and support exposure relate to feature adoption and repeat behavior?",
        "ko": "질문: 고객 가치 구간과 고객지원 경험은 기능 사용 및 반복 행동과 어떻게 연결되는가?",
    },
    "value_finding_title": {"en": "High-value users adopt deeper workflow features", "ko": "고가치 사용자는 고급 기능을 더 많이 사용"},
    "value_finding_text": {
        "en": "Higher-volume segments show much deeper adoption of target-rate and rate-alert features.",
        "ko": "거래 규모가 큰 고객 구간일수록 목표 환율과 환율 알림 기능 사용률이 높습니다.",
    },
    "support_caveat_title": {"en": "Support exposure can reflect engagement", "ko": "고객지원 이력은 참여도가 높은 사용자의 신호일 수 있음"},
    "support_caveat_text": {
        "en": "Support-ticket exposure may reflect higher engagement, not necessarily churn risk or a retention lift.",
        "ko": "고객지원 티켓은 이탈 위험이나 리텐션 개선 효과라기보다, 높은 참여도의 신호일 수 있습니다.",
    },
    "method_subtitle": {
        "en": "How the portfolio case study is structured and what data products feed the dashboard.",
        "ko": "이 포트폴리오 분석이 어떻게 구성되었고 어떤 데이터 산출물이 대시보드를 구성하는지 설명합니다.",
    },
    "modeling_snapshots": {"en": "Modeling snapshots", "ko": "모델링 스냅샷"},
    "modeled_users": {"en": "Modeled users", "ko": "모델링 대상 사용자"},
    "positive_target_rate": {"en": "Positive target rate", "ko": "양성 타깃 비율"},
    "avg_failed_ratio": {"en": "Avg failed ratio 90d", "ko": "90일 평균 실패 비율"},
    "csv_files_used": {"en": "CSV Files Used", "ko": "사용된 CSV 파일"},
}

KICKER_LABELS = {
    "Finding": {"en": "Finding", "ko": "핵심 발견"},
    "Funnel": {"en": "Funnel", "ko": "퍼널"},
    "Retention": {"en": "Retention", "ko": "리텐션"},
    "Interpretation": {"en": "Interpretation", "ko": "해석"},
    "Recommendation": {"en": "Recommendation", "ko": "제안"},
    "Caveat": {"en": "Caveat", "ko": "주의사항"},
}


st.set_page_config(
    page_title="FX Fintech Product Analytics",
    layout="wide",
)


@st.cache_data
def load_csv(file_name: str) -> pd.DataFrame:
    path = CSV_DIR / file_name

    if not path.exists():
        raise FileNotFoundError(f"Missing required CSV: {path}")

    return pd.read_csv(path)


def clean_label(value: str, lang: str = "en") -> str:
    text = str(value)
    labels = CHANNEL_LABELS_KO if lang == "ko" else CHANNEL_LABELS
    return labels.get(text, text.replace("_", " ").capitalize())


def t(key: str, lang: str) -> str:
    return TEXT.get(key, {}).get(lang, TEXT.get(key, {}).get("en", key))


def format_number(value: float) -> str:
    return f"{value:,.0f}"


def format_percent(value: float) -> str:
    return f"{value:.2f}%"


def format_compact_money(value: float) -> str:
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.1f}B"
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    return format_number(value)


def inject_css() -> None:
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: {COLOR_PAGE};
            color: {COLOR_TEXT};
        }}

        [data-testid="stHeader"] {{
            background: rgba(247, 249, 252, 0.88);
        }}

        h1, h2, h3 {{
            color: {COLOR_TEXT};
            letter-spacing: 0;
        }}

        .block-container {{
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1480px;
        }}

        .hero {{
            border: 1px solid {COLOR_BORDER};
            border-radius: 12px;
            background: linear-gradient(135deg, #FFFFFF 0%, #EEF6F6 100%);
            padding: 28px 30px;
            margin-bottom: 18px;
        }}

        .hero h1 {{
            margin: 0 0 8px 0;
            font-size: 2.2rem;
            line-height: 1.1;
        }}

        .hero p {{
            margin: 0;
            color: {COLOR_MUTED};
            font-size: 1rem;
        }}

        .synthetic-note {{
            display: inline-block;
            margin-top: 14px;
            padding: 7px 10px;
            border: 1px solid #CBD5E1;
            border-radius: 8px;
            background: #F8FAFC;
            color: #334155;
            font-size: 0.86rem;
        }}

        .metric-card {{
            min-height: 116px;
            border: 1px solid {COLOR_BORDER};
            border-radius: 10px;
            background: {COLOR_CARD};
            padding: 16px 16px 14px 16px;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
        }}

        .metric-label {{
            color: {COLOR_MUTED};
            font-size: 0.82rem;
            font-weight: 650;
            text-transform: uppercase;
            letter-spacing: 0.03em;
            margin-bottom: 8px;
        }}

        .metric-value {{
            color: {COLOR_TEXT};
            font-size: 1.7rem;
            line-height: 1.15;
            font-weight: 760;
            margin-bottom: 6px;
        }}

        .metric-help {{
            color: {COLOR_MUTED};
            font-size: 0.82rem;
            line-height: 1.35;
        }}

        .section-title {{
            margin-top: 18px;
            margin-bottom: 4px;
            font-size: 1.25rem;
            font-weight: 760;
            color: {COLOR_TEXT};
        }}

        .section-subtitle {{
            margin-bottom: 14px;
            color: {COLOR_MUTED};
            font-size: 0.96rem;
        }}

        .insight-box {{
            border: 1px solid {COLOR_BORDER};
            border-left: 4px solid {COLOR_TEAL};
            border-radius: 10px;
            background: {COLOR_CARD};
            padding: 14px 15px;
            min-height: 118px;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
        }}

        .insight-kicker {{
            color: {COLOR_TEAL};
            font-size: 0.78rem;
            font-weight: 760;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 6px;
        }}

        .insight-title {{
            color: {COLOR_TEXT};
            font-size: 1.02rem;
            font-weight: 740;
            margin-bottom: 5px;
        }}

        .insight-text {{
            color: {COLOR_MUTED};
            font-size: 0.92rem;
            line-height: 1.45;
        }}

        .method-card {{
            border: 1px solid {COLOR_BORDER};
            border-radius: 10px;
            background: {COLOR_CARD};
            padding: 16px 17px;
            min-height: 150px;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
        }}

        .method-card h3 {{
            margin-top: 0;
            margin-bottom: 8px;
            font-size: 1.02rem;
        }}

        .method-card p, .method-card li {{
            color: {COLOR_MUTED};
            font-size: 0.92rem;
            line-height: 1.45;
        }}

        div[data-testid="stTabs"] button {{
            color: {COLOR_TEXT};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(label: str, value: str, help_text: str = "") -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-help">{help_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def insight_box(kicker: str, title: str, text: str, lang: str = "en") -> None:
    kicker_label = KICKER_LABELS.get(kicker, {"en": kicker}).get(lang, kicker)
    st.markdown(
        f"""
        <div class="insight-box">
            <div class="insight-kicker">{kicker_label}</div>
            <div class="insight-title">{title}</div>
            <div class="insight-text">{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="section-title">{title}</div>
        <div class="section-subtitle">{subtitle}</div>
        """,
        unsafe_allow_html=True,
    )


def style_plotly(fig: go.Figure, height: int = 430) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=20, r=20, t=62, b=42),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=COLOR_TEXT, size=13),
        title=dict(font=dict(color=COLOR_TEXT, size=18), x=0),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.03,
            xanchor="left",
            x=0,
            font=dict(color=COLOR_TEXT),
        ),
        hoverlabel=dict(bgcolor="white", font_size=12, font_color=COLOR_TEXT),
    )
    fig.update_xaxes(
        showgrid=False,
        linecolor=COLOR_BORDER,
        tickfont=dict(color=COLOR_TEXT),
        title_font=dict(color=COLOR_MUTED),
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor=COLOR_BORDER,
        zeroline=False,
        linecolor=COLOR_BORDER,
        tickfont=dict(color=COLOR_TEXT),
        title_font=dict(color=COLOR_MUTED),
    )
    return fig


def product_funnel_chart(df: pd.DataFrame, lang: str) -> go.Figure:
    steps = [
        ("Valid signups" if lang == "en" else "유효 가입자", "valid_signups"),
        ("KYC completed" if lang == "en" else "KYC 완료", "kyc_completed"),
        ("Bank linked" if lang == "en" else "계좌 연결", "bank_linked"),
        ("First exchange" if lang == "en" else "첫 환전", "first_successful_exchange"),
        ("Activated 14d" if lang == "en" else "14일 활성화", "activated_within_14_days"),
    ]
    chart_df = pd.DataFrame(
        {
            "step": [label for label, _ in steps],
            "users": [df.loc[0, column] for _, column in steps],
        }
    )

    fig = px.bar(
        chart_df,
        x="step",
        y="users",
        text="users",
        color_discrete_sequence=[COLOR_TEAL],
        title="Product Onboarding Funnel" if lang == "en" else "제품 온보딩 퍼널",
    )
    fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside", cliponaxis=False)
    fig.update_yaxes(title="Users" if lang == "en" else "사용자 수")
    fig.update_xaxes(title="")
    return style_plotly(fig)


def monthly_signups_activation_chart(df: pd.DataFrame, lang: str) -> go.Figure:
    chart_df = df.copy()
    chart_df["signup_month"] = pd.to_datetime(chart_df["signup_month"])

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_bar(
        x=chart_df["signup_month"],
        y=chart_df["valid_signups"],
        name="Valid signups" if lang == "en" else "유효 가입자",
        marker_color=COLOR_TEAL,
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=chart_df["signup_month"],
            y=chart_df["activation_rate_14d"],
            name="14-day activation rate" if lang == "en" else "14일 활성화율",
            mode="lines+markers",
            line=dict(color=COLOR_ORANGE, width=3),
            marker=dict(size=8),
        ),
        secondary_y=True,
    )
    fig.update_layout(title="Monthly Signups and 14-Day Activation Rate" if lang == "en" else "월별 가입자와 14일 활성화율")
    fig.update_yaxes(title_text="Valid signups" if lang == "en" else "유효 가입자", secondary_y=False)
    fig.update_yaxes(title_text="Activation rate" if lang == "en" else "활성화율", ticksuffix="%", secondary_y=True)
    fig.update_xaxes(title="")
    return style_plotly(fig, height=460)


def horizontal_rate_chart(
    df: pd.DataFrame,
    label_column: str,
    value_column: str,
    title: str,
    color: str,
    x_range: list[float] | None = None,
    height: int = 430,
) -> go.Figure:
    chart_df = df.copy().sort_values(value_column, ascending=True)

    fig = px.bar(
        chart_df,
        x=value_column,
        y=label_column,
        orientation="h",
        text=value_column,
        color_discrete_sequence=[color],
        title=title,
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside", cliponaxis=False)
    fig.update_xaxes(title="", ticksuffix="%", range=x_range)
    fig.update_yaxes(title="")
    return style_plotly(fig, height=height)


def fx_regime_chart(behavior: pd.DataFrame, activity: pd.DataFrame, lang: str) -> go.Figure:
    chart_df = activity.merge(
        behavior[["market_regime_at_transaction", "success_rate"]],
        left_on="market_regime",
        right_on="market_regime_at_transaction",
        how="left",
    )
    regime_order = ["low", "normal", "high"]
    chart_df["market_regime"] = pd.Categorical(
        chart_df["market_regime"],
        categories=regime_order,
        ordered=True,
    )
    chart_df = chart_df.sort_values("market_regime")
    if lang == "ko":
        chart_df["regime_label"] = chart_df["market_regime"].astype(str).replace(
            {"low": "낮음", "normal": "보통", "high": "높음"}
        )
    else:
        chart_df["regime_label"] = chart_df["market_regime"].map(clean_label)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_bar(
        x=chart_df["regime_label"],
        y=chart_df["attempts_per_regime_hour"],
        text=chart_df["attempts_per_regime_hour"],
        texttemplate="%{text:.2f}",
        textposition="outside",
        name="Attempts per regime hour" if lang == "en" else "구간 시간당 거래 시도",
        marker_color=COLOR_TEAL,
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=chart_df["regime_label"],
            y=chart_df["success_rate"],
            mode="lines+markers",
            name="Success rate" if lang == "en" else "성공률",
            line=dict(color=COLOR_ORANGE, width=3),
            marker=dict(size=9),
        ),
        secondary_y=True,
    )
    fig.update_layout(title="FX Regime Activity and Exchange Success" if lang == "en" else "환율 변동성 구간별 거래 활동과 성공률")
    fig.update_yaxes(title_text="Attempts per regime hour" if lang == "en" else "구간 시간당 거래 시도", secondary_y=False)
    fig.update_yaxes(title_text="Success rate" if lang == "en" else "성공률", ticksuffix="%", range=[85, 95], secondary_y=True)
    fig.update_xaxes(title="FX regime" if lang == "en" else "환율 변동성 구간")
    return style_plotly(fig, height=440)


def cohort_heatmap(df: pd.DataFrame, lang: str, exclude_m0: bool = True) -> go.Figure:
    chart_df = df.copy()

    if exclude_m0:
        chart_df = chart_df[chart_df["months_since_first_transaction"] > 0]

    chart_df["cohort_month"] = pd.to_datetime(chart_df["cohort_month"]).dt.strftime("%Y-%m")
    pivot = chart_df.pivot(
        index="cohort_month",
        columns="months_since_first_transaction",
        values="retention_rate",
    ).sort_index()

    fig = px.imshow(
        pivot,
        aspect="auto",
        color_continuous_scale="YlGnBu",
        zmin=30 if exclude_m0 else 0,
        zmax=75 if exclude_m0 else 100,
        labels={
            "x": "Months since first transaction" if lang == "en" else "첫 거래 이후 경과 월",
            "y": "First transaction cohort" if lang == "en" else "첫 거래 코호트",
            "color": "Retention rate" if lang == "en" else "리텐션율",
        },
        title=(
            "Cohort Retention Heatmap Excluding M0"
            if lang == "en" and exclude_m0
            else "Cohort Retention Heatmap"
            if lang == "en"
            else "M0 제외 코호트 리텐션 히트맵"
            if exclude_m0
            else "코호트 리텐션 히트맵"
        ),
    )
    fig.update_coloraxes(colorbar_ticksuffix="%")
    return style_plotly(fig, height=700)


def customer_value_chart(df: pd.DataFrame, lang: str) -> go.Figure:
    chart_df = df.copy()
    chart_df["value_segment_label"] = chart_df["value_segment"].replace(
        {
            "Q1 lowest volume": "Q1 lowest volume",
            "Q4 highest volume": "Q4 highest volume",
        }
    )

    fig = go.Figure()
    fig.add_bar(
        x=chart_df["value_segment_label"],
        y=chart_df["target_rate_adoption_rate"],
        name="Target-rate" if lang == "en" else "목표 환율",
        marker_color=COLOR_TEAL,
    )
    fig.add_bar(
        x=chart_df["value_segment_label"],
        y=chart_df["rate_alert_adoption_rate"],
        name="Rate alert" if lang == "en" else "환율 알림",
        marker_color=COLOR_NAVY,
    )
    fig.update_layout(title="Feature Adoption by Customer Value Segment" if lang == "en" else "고객 가치 구간별 기능 사용률", barmode="group")
    fig.update_yaxes(title="Adoption rate" if lang == "en" else "기능 사용률", ticksuffix="%", range=[0, 100])
    fig.update_xaxes(title="")
    return style_plotly(fig)


def support_ticket_chart(df: pd.DataFrame, lang: str) -> go.Figure:
    group_order = ["No support ticket", "One support ticket", "Multiple support tickets"]
    chart_df = df.copy()
    if lang == "ko":
        chart_df["support_group"] = chart_df["support_group"].replace(
            {
                "No support ticket": "고객지원 티켓 없음",
                "One support ticket": "고객지원 티켓 1건",
                "Multiple support tickets": "고객지원 티켓 여러 건",
            }
        )
        group_order = ["고객지원 티켓 없음", "고객지원 티켓 1건", "고객지원 티켓 여러 건"]
    chart_df["support_group"] = pd.Categorical(
        chart_df["support_group"],
        categories=group_order,
        ordered=True,
    )
    chart_df = chart_df.sort_values("support_group")

    fig = px.bar(
        chart_df,
        x="support_group",
        y="d30_repeat_rate",
        text="d30_repeat_rate",
        color_discrete_sequence=[COLOR_ROSE],
        title="D30 Repeat Rate by Support Ticket Exposure" if lang == "en" else "고객지원 경험별 30일 반복률",
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside", cliponaxis=False)
    fig.update_yaxes(title="D30 repeat rate" if lang == "en" else "30일 반복률", ticksuffix="%", range=[0, 55])
    fig.update_xaxes(title="")
    return style_plotly(fig)


def render_header(lang: str) -> None:
    st.markdown(
        f"""
        <div class="hero">
            <h1>{t("hero_title", lang)}</h1>
            <p>{t("hero_subtitle", lang)}</p>
            <div class="synthetic-note">
                {t("synthetic_note", lang)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpis(lifecycle: pd.DataFrame, product_funnel: pd.DataFrame, lang: str) -> None:
    summary = lifecycle.loc[0]
    funnel = product_funnel.loc[0]

    cols = st.columns(5)
    with cols[0]:
        render_metric_card(
            t("valid_users", lang),
            format_number(summary["valid_onboarding_users"]),
            t("valid_users_help", lang),
        )
    with cols[1]:
        render_metric_card(
            t("activation_14d", lang),
            format_percent(summary["activation_rate_14d"]),
            t("activation_help", lang),
        )
    with cols[2]:
        render_metric_card(
            t("first_exchanges", lang),
            format_number(funnel["first_successful_exchange"]),
            t("first_exchange_help", lang),
        )
    with cols[3]:
        render_metric_card(
            t("target_rate_users", lang),
            format_number(summary["target_rate_users"]),
            t("target_rate_help", lang),
        )
    with cols[4]:
        render_metric_card(
            t("rate_alert_users", lang),
            format_number(summary["rate_alert_users"]),
            t("rate_alert_help", lang),
        )


def render_overview(product_funnel: pd.DataFrame, monthly: pd.DataFrame, lang: str) -> None:
    section_header(
        t("tab_overview", lang),
        t("overview_subtitle", lang),
    )
    cols = st.columns(3)
    with cols[0]:
        insight_box(
            "Finding",
            t("overview_finding_title", lang),
            t("overview_finding_text", lang),
            lang,
        )
    with cols[1]:
        insight_box(
            "Funnel",
            t("overview_funnel_title", lang),
            t("overview_funnel_text", lang),
            lang,
        )
    with cols[2]:
        insight_box(
            "Retention",
            t("overview_retention_title", lang),
            t("overview_retention_text", lang),
            lang,
        )

    left, right = st.columns([1, 1])
    with left:
        st.plotly_chart(product_funnel_chart(product_funnel, lang), width="stretch")
    with right:
        st.plotly_chart(monthly_signups_activation_chart(monthly, lang), width="stretch")


def render_acquisition(funnel_channel: pd.DataFrame, repeat_channel: pd.DataFrame, lang: str) -> None:
    section_header(
        t("tab_acquisition", lang),
        t("acquisition_subtitle", lang),
    )
    left, right = st.columns([1, 1])
    with left:
        insight_box(
            "Finding",
            t("acquisition_finding_title", lang),
            t("acquisition_finding_text", lang),
            lang,
        )
        st.plotly_chart(
            horizontal_rate_chart(
                funnel_channel,
                "channel_label",
                "activation_rate_14d",
                "14-Day Activation Rate by Acquisition Channel" if lang == "en" else "유입 채널별 14일 활성화율",
                COLOR_TEAL,
                x_range=[0, 28],
            ),
            width="stretch",
        )
    with right:
        insight_box(
            "Interpretation",
            t("repeat_finding_title", lang),
            t("repeat_finding_text", lang),
            lang,
        )
        st.plotly_chart(
            horizontal_rate_chart(
                repeat_channel,
                "channel_label",
                "d30_repeat_rate",
                "D30 Repeat Rate by Acquisition Channel" if lang == "en" else "유입 채널별 30일 반복률",
                COLOR_ORANGE,
                x_range=[0, 50],
            ),
            width="stretch",
        )


def render_retention(feature_combo: pd.DataFrame, cohort: pd.DataFrame, lang: str) -> None:
    section_header(
        t("tab_retention", lang),
        t("retention_subtitle", lang),
    )
    left, right = st.columns([0.9, 1.1])
    with left:
        insight_box(
            "Finding",
            t("feature_finding_title", lang),
            t("feature_finding_text", lang),
            lang,
        )
        st.plotly_chart(
            horizontal_rate_chart(
                feature_combo,
                "feature_group",
                "d30_repeat_rate",
                "D30 Repeat Rate by Feature Adoption" if lang == "en" else "기능 사용 그룹별 30일 반복률",
                COLOR_NAVY,
                x_range=[0, 65],
            ),
            width="stretch",
        )
        insight_box(
            "Recommendation",
            t("feature_reco_title", lang),
            t("feature_reco_text", lang),
            lang,
        )
    with right:
        st.plotly_chart(cohort_heatmap(cohort, lang, exclude_m0=True), width="stretch")


def render_fx_regime(fx_behavior: pd.DataFrame, fx_activity: pd.DataFrame, failure: pd.DataFrame, lang: str) -> None:
    section_header(
        t("tab_fx", lang),
        t("fx_subtitle", lang),
    )
    insight_box(
        "Finding",
        t("fx_finding_title", lang),
        t("fx_finding_text", lang),
        lang,
    )
    st.plotly_chart(fx_regime_chart(fx_behavior, fx_activity, lang), width="stretch")

    st.markdown(f"#### {t('failure_table', lang)}")
    st.dataframe(
        failure,
        width="stretch",
        hide_index=True,
    )


def render_value_support(value_segments: pd.DataFrame, support: pd.DataFrame, lang: str) -> None:
    section_header(
        t("tab_value", lang),
        t("value_subtitle", lang),
    )
    left, right = st.columns([1, 1])
    with left:
        insight_box(
            "Finding",
            t("value_finding_title", lang),
            t("value_finding_text", lang),
            lang,
        )
        st.plotly_chart(customer_value_chart(value_segments, lang), width="stretch")
    with right:
        insight_box(
            "Caveat",
            t("support_caveat_title", lang),
            t("support_caveat_text", lang),
            lang,
        )
        st.plotly_chart(support_ticket_chart(support, lang), width="stretch")


def render_data_methodology(modeling_check: pd.DataFrame, lang: str) -> None:
    section_header(
        t("tab_method", lang),
        t("method_subtitle", lang),
    )
    check = modeling_check.loc[0]

    cols = st.columns(4)
    with cols[0]:
        render_metric_card(t("modeling_snapshots", lang), format_number(check["snapshot_rows"]), "User-month rows." if lang == "en" else "사용자-월 단위 행 수입니다.")
    with cols[1]:
        render_metric_card(t("modeled_users", lang), format_number(check["users"]), "Distinct users in snapshots." if lang == "en" else "스냅샷에 포함된 고유 사용자 수입니다.")
    with cols[2]:
        render_metric_card(t("positive_target_rate", lang), format_percent(check["positive_target_rate"]), "Repeat target share." if lang == "en" else "반복 사용 타깃 비율입니다.")
    with cols[3]:
        render_metric_card(t("avg_failed_ratio", lang), f"{check['avg_failed_ratio_90d']:.3f}", "Recent failed exchange ratio." if lang == "en" else "최근 90일 평균 실패 거래 비율입니다.")

    a, b, c = st.columns(3)
    with a:
        st.markdown(
            """
            <div class="method-card">
                <h3>{"Data Source Summary" if lang == "en" else "데이터 소스 요약"}</h3>
                <p>{"SQLite database with users, events, transactions, FX rates, marketing spend, support tickets, and user-month modeling snapshots." if lang == "en" else "사용자, 이벤트, 거래, 환율, 마케팅 비용, 고객지원 티켓, 사용자-월 모델링 스냅샷으로 구성된 SQLite 데이터베이스입니다."}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with b:
        st.markdown(
            """
            <div class="method-card">
                <h3>{"SQL Mart Summary" if lang == "en" else "SQL 마트 요약"}</h3>
                <p>{"The dashboard is built from SQL marts and analysis queries exported from SQLite into dashboard-ready CSV files." if lang == "en" else "대시보드는 SQLite에서 SQL 마트와 분석 쿼리를 실행한 뒤, 대시보드용 CSV로 추출한 데이터를 사용합니다."}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c:
        st.markdown(
            """
            <div class="method-card">
                <h3>{"Synthetic Dataset Caveat" if lang == "en" else "합성 데이터 안내"}</h3>
                <p>{"This is a synthetic portfolio dataset for demonstration. Results should be interpreted as case-study analytics, not actual company performance." if lang == "en" else "이 데이터는 포트폴리오 시연을 위한 합성 데이터입니다. 결과는 실제 회사 성과가 아니라 분석 사례로 해석해야 합니다."}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(f"#### {t('csv_files_used', lang)}")
    csv_files = [
        ("Product funnel", "product_funnel.csv"),
        ("Channel funnel", "funnel_by_acquisition_channel.csv"),
        ("D30 repeat by channel", "d30_repeat_by_channel.csv"),
        ("Feature retention", "feature_combination_retention.csv"),
        ("FX regime behavior", "fx_regime_behavior.csv"),
        ("FX normalized activity", "fx_regime_normalized_activity.csv"),
        ("Failure reasons", "failure_reason_by_regime.csv"),
        ("Monthly product trend", "monthly_product_trend.csv"),
        ("Cohort retention", "cohort_retention.csv"),
        ("Customer value segments", "customer_value_segmentation.csv"),
        ("Support ticket impact", "support_ticket_impact.csv"),
        ("Modeling table check", "modeling_table_check.csv"),
        ("Lifecycle summary", "user_lifecycle_summary.csv"),
    ]
    st.dataframe(
        pd.DataFrame(csv_files, columns=["Dataset", "CSV file"]),
        width="stretch",
        hide_index=True,
    )


def load_dashboard_data() -> dict[str, pd.DataFrame]:
    data = {
        "product_funnel": load_csv("product_funnel.csv"),
        "lifecycle": load_csv("user_lifecycle_summary.csv"),
        "monthly": load_csv("monthly_product_trend.csv"),
        "funnel_channel": load_csv("funnel_by_acquisition_channel.csv"),
        "repeat_channel": load_csv("d30_repeat_by_channel.csv"),
        "feature_combo": load_csv("feature_combination_retention.csv"),
        "cohort": load_csv("cohort_retention.csv"),
        "fx_behavior": load_csv("fx_regime_behavior.csv"),
        "fx_activity": load_csv("fx_regime_normalized_activity.csv"),
        "failure": load_csv("failure_reason_by_regime.csv"),
        "value_segments": load_csv("customer_value_segmentation.csv"),
        "support": load_csv("support_ticket_impact.csv"),
        "modeling_check": load_csv("modeling_table_check.csv"),
    }

    return data


def main() -> None:
    inject_css()
    data = load_dashboard_data()
    language_label = st.sidebar.radio("Language / 언어", list(LANGUAGE_OPTIONS.keys()), horizontal=True)
    lang = LANGUAGE_OPTIONS[language_label]

    data["funnel_channel"]["channel_label"] = data["funnel_channel"]["acquisition_channel"].map(
        lambda value: clean_label(value, lang)
    )
    data["repeat_channel"]["channel_label"] = data["repeat_channel"]["acquisition_channel"].map(
        lambda value: clean_label(value, lang)
    )

    render_header(lang)
    render_kpis(data["lifecycle"], data["product_funnel"], lang)

    overview_tab, acquisition_tab, retention_tab, fx_tab, value_tab, method_tab = st.tabs(
        [
            t("tab_overview", lang),
            t("tab_acquisition", lang),
            t("tab_retention", lang),
            t("tab_fx", lang),
            t("tab_value", lang),
            t("tab_method", lang),
        ]
    )

    with overview_tab:
        render_overview(data["product_funnel"], data["monthly"], lang)

    with acquisition_tab:
        render_acquisition(data["funnel_channel"], data["repeat_channel"], lang)

    with retention_tab:
        render_retention(data["feature_combo"], data["cohort"], lang)

    with fx_tab:
        render_fx_regime(data["fx_behavior"], data["fx_activity"], data["failure"], lang)

    with value_tab:
        render_value_support(data["value_segments"], data["support"], lang)

    with method_tab:
        render_data_methodology(data["modeling_check"], lang)


if __name__ == "__main__":
    main()
