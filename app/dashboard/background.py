"""Low-opacity animated background for the trading terminal.

Reuses the existing particle-network animation (assets/canvas.js)
unchanged. The only job here is *wiring*: `st.components.v1.html`
sandboxes content inside a small iframe, so a naive `position: fixed`
canvas would be clipped to that iframe's own height instead of
covering the real page. This injects the canvas directly into the
parent Streamlit document instead, and guards against re-injecting
a second animation loop on every rerun.
"""

from pathlib import Path

import streamlit.components.v1 as components

_CANVAS_ID = "bg-canvas"

# Spec calls for a subtle background at ~5-10% opacity so it never
# competes with charts/tables for attention.
_DEFAULT_OPACITY = 0.07


def load_background(opacity: float = _DEFAULT_OPACITY) -> None:
    """Inject the animated particle-network background once per page."""
    canvas_file = Path(__file__).parent / "assets" / "canvas.js"
    if not canvas_file.exists():
        return

    particle_js = canvas_file.read_bytes().decode("utf-8-sig")

    bootstrap = f"""
    <script>
    (function() {{
        const parentDoc = window.parent.document;

        // Guard: reruns re-execute this component, so bail out if the
        // canvas + animation loop are already running to avoid stacking
        // duplicate loops (perf degradation) or memory leaks.
        if (parentDoc.getElementById("{_CANVAS_ID}")) return;

        const style = parentDoc.createElement("style");
        style.textContent =
            "#{_CANVAS_ID} {{ position: fixed; inset: 0; width: 100vw; " +
            "height: 100vh; z-index: -999; pointer-events: none; " +
            "opacity: {opacity}; }}";
        parentDoc.head.appendChild(style);

        const canvas = parentDoc.createElement("canvas");
        canvas.id = "{_CANVAS_ID}";
        parentDoc.body.appendChild(canvas);

        // Run the unmodified canvas.js body with document/window/rAF
        // rebound to the parent frame, so it draws on the real page
        // instead of the invisible sandbox iframe.
        (function(document, window, requestAnimationFrame) {{
{particle_js}
        }})(parentDoc, window.parent, window.parent.requestAnimationFrame.bind(window.parent));
    }})();
    </script>
    """

    components.html(bootstrap, height=0, scrolling=False)
