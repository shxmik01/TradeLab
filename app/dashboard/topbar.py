"""Live ticker + world clock + market session status bar.

Ticker prices come from the `prices` dict already fetched for the
dashboard payload — this widget does not poll the backend on its own,
so it only refreshes when the page reruns. The clock and session dots
DO tick live every second, purely client-side via JS, since that needs
no server round-trip.

Session hours are standard trading-session approximations with no DST
adjustment: Sydney 22:00-07:00 UTC, Tokyo 00:00-09:00 UTC,
London 08:00-17:00 UTC, New York 13:00-22:00 UTC.
"""

from __future__ import annotations

import json

import streamlit.components.v1 as components

_TEMPLATE = """
<div id="shxmik-topbar">
  <style>
    #shxmik-topbar { font-family: 'Inter', 'Segoe UI', sans-serif; color: #f2f6ff; }
    .ticker-wrap {
        overflow: hidden;
        white-space: nowrap;
        border-top: 1px solid #20242D;
        border-bottom: 1px solid #20242D;
        padding: 8px 0;
    }
    .ticker-track { display: inline-block; padding-left: 100%; animation: ticker-scroll 30s linear infinite; }
    @keyframes ticker-scroll {
        0%   { transform: translate(0, 0); }
        100% { transform: translate(-100%, 0); }
    }
    .ticker-item { display: inline-block; margin-right: 40px; font-size: 0.85rem; font-weight: 600; }
    .sessions-row {
        display: flex; justify-content: center; align-items: center;
        gap: 22px; flex-wrap: wrap; padding: 10px 0 2px; font-size: 0.8rem;
    }
    .utc-clock { font-weight: 700; letter-spacing: 0.05em; color: #00c8ff; }
  </style>

  <div class="ticker-wrap"><div class="ticker-track" id="ticker-track"></div></div>

  <div class="sessions-row">
    <span>UTC <span class="utc-clock" id="utc-clock">--:--:--</span></span>
    <span id="sess-sydney">Sydney --:--</span>
    <span id="sess-tokyo">Tokyo --:--</span>
    <span id="sess-london">London --:--</span>
    <span id="sess-newyork">New York --:--</span>
  </div>
</div>

<script>
(function() {
    const tickerData = __TICKER_JSON__;
    const track = document.getElementById("ticker-track");

    if (tickerData.length === 0) {
        track.innerHTML = "<span class='ticker-item'>No live prices available</span>";
    } else {
        const items = tickerData.map(function(t) {
            const price = Number(t.price).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
            return "<span class='ticker-item'>" + t.symbol + " <b>$" + price + "</b></span>";
        });
        track.innerHTML = items.join("") + items.join(""); // duplicated for a seamless loop
    }

    const sessions = [
        { id: "sess-sydney",  label: "Sydney",   tz: "Australia/Sydney", start: 22, end: 7  },
        { id: "sess-tokyo",   label: "Tokyo",    tz: "Asia/Tokyo",       start: 0,  end: 9  },
        { id: "sess-london",  label: "London",   tz: "Europe/London",    start: 8,  end: 17 },
        { id: "sess-newyork", label: "New York", tz: "America/New_York", start: 13, end: 22 }
    ];

    function isOpen(hourDecimal, start, end) {
        if (start < end) return hourDecimal >= start && hourDecimal < end;
        return hourDecimal >= start || hourDecimal < end; // wraps midnight (Sydney)
    }

    function nearBoundary(hourDecimal, start, end) {
        const dist = Math.min(
            Math.abs(hourDecimal - start),
            Math.abs(hourDecimal - end),
            Math.abs(hourDecimal - start + 24),
            Math.abs(hourDecimal - end + 24)
        );
        return dist <= 1; // within 1 hour of open/close
    }

    function tick() {
        const now = new Date();
        document.getElementById("utc-clock").textContent = now.toISOString().substr(11, 8);

        const utcHourDecimal = now.getUTCHours() + now.getUTCMinutes() / 60;

        sessions.forEach(function(s) {
            const open = isOpen(utcHourDecimal, s.start, s.end);
            const near = nearBoundary(utcHourDecimal, s.start, s.end);
            const dot = open ? (near ? "🟡" : "🟢") : "🔴";
            const localTime = now.toLocaleTimeString("en-US", { timeZone: s.tz, hour: "2-digit", minute: "2-digit", hour12: false });
            document.getElementById(s.id).textContent = dot + " " + s.label + " " + localTime;
        });
    }

    tick();
    setInterval(tick, 1000);
})();
</script>
"""


def render_topbar(prices: dict) -> None:
    """Render the ticker + world clock + session status bar."""
    ticker_items = [{"symbol": symbol, "price": price} for symbol, price in prices.items()]
    html = _TEMPLATE.replace("__TICKER_JSON__", json.dumps(ticker_items))
    components.html(html, height=110, scrolling=False)
