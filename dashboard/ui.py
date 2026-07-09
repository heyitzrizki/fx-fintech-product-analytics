import streamlit as st


def page_intro(title: str, metric: str, decision: str, caveat: str) -> None:
    st.title(title)
    st.caption(f"Metric: {metric}")
    st.info(f"Decision: {decision}")
    st.caption(f"Caveat: {caveat}")


def pattern(text: str) -> None:
    st.markdown(f"**Pattern:** {text}")


def percent(value: float) -> str:
    return f"{value:.1f}%"
