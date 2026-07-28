"""Reusable placeholder panel for markets that aren't built yet (Forex, Futures)."""

from __future__ import annotations

import streamlit as st


def render_coming_soon(market_name: str, icon: str, planned_features: list[str]) -> None:
    """Render a "Coming Soon" panel listing planned features for a future market."""
    st.markdown(f"### {icon} {market_name}")
    st.info(f"{market_name} paper trading isn't available yet — it's on the roadmap.")

    st.markdown("**Planned features:**")
    for feature in planned_features:
        st.markdown(f"- {feature}")
