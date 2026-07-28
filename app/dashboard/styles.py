"""CSS loader for the trading dashboard.

The previous version of this module was accidentally saved as raw CSS
instead of Python, which made `app_refactored.py`'s
`from app.dashboard.styles import load_css` fail immediately on import.
This module now does one job: read the stylesheet from
`assets/dashboard.css` and inject it into the page via `st.markdown`.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

_CSS_PATH = Path(__file__).parent / "assets" / "dashboard.css"

# Minimal fallback so the app still renders (unstyled but functional)
# if the CSS asset is ever missing or fails to read.
_FALLBACK_CSS = """
.stApp { background: #0d1424; color: #f2f6ff; }
"""


def load_css() -> None:
    """Inject the dashboard stylesheet into the current Streamlit page."""
    try:
        css = _CSS_PATH.read_text(encoding="utf-8-sig")
    except OSError:
        css = _FALLBACK_CSS

    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
