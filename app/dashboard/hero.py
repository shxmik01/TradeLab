"""Dashboard hero banner: brand, tagline, and market-status badges."""

from __future__ import annotations

import streamlit as st

from app.dashboard.background import load_background


def render_hero() -> None:
    """Render the top banner shown at the head of the Dashboard page."""
    # load_background()
    st.markdown(
        """
        <div class="hero-banner">
            <div class="hero-title">🚀 Shxmik TradeLab</div>
            <div class="hero-tagline">Professional Trading Platform</div>
            <div class="hero-motto">Trade &bull; Learn &bull; Analyze &bull; Improve</div>
            <div class="hero-divider"></div>
            <div class="hero-badges">
                <span class="hero-badge hero-badge-live">🟢 Crypto</span>
                <span class="hero-badge hero-badge-soon">🚧 Forex (Coming Soon)</span>
                <span class="hero-badge hero-badge-soon">🚧 Futures (Coming Soon)</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
