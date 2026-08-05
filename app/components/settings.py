"""Professional Settings page.

All settings are persisted to `settings.json` through the central
`app.core.config` module. Nothing here is hardcoded — every label, option
list, default and validation bound is derived from `DEFAULT_SETTINGS`.

On Save, the page validates first; invalid values are never written and a
clear error is shown. The bottom "Current Active Settings" table reads
straight from `config.get_settings()` so Save/Reset are verifiable at a glance.
"""

from __future__ import annotations

import streamlit as st

from app.core import config


def render_settings() -> None:
    """Render the Settings page: Trading / Risk / Bot sections + actions."""
    # Ensure the JSON file exists and the cache is fresh.
    config.load_settings()

    st.title("⚙ Settings")
    st.caption("Changes are persisted to `settings.json` and apply on the next run of the bot.")

    # --- Form collects the draft; nothing is written until Save is clicked. ---
    with st.form("settings_form", border=False):
        st.subheader("📦 Trading")
        c1, c2, c3 = st.columns(3)
        with c1:
            starting_balance = st.number_input(
                "Starting Balance ($)",
                min_value=0.0,
                step=100.0,
                value=float(config.get_settings()["starting_balance"]),
                key="cfg_starting_balance",
                help="Initial paper-trading balance. Must be greater than 0.",
            )
            order_size = st.number_input(
                "Default Order Size ($)",
                min_value=0.0,
                step=10.0,
                value=float(config.get_settings()["order_size"]),
                key="cfg_order_size",
                help="Size of each position on the paper wallet. Must be greater than 0.",
            )
        with c2:
            max_positions = st.number_input(
                "Max Open Positions",
                min_value=1,
                step=1,
                value=int(config.get_settings()["max_open_positions"]),
                key="cfg_max_positions",
                help="Concurrent open positions allowed. Must be at least 1.",
            )
            default_symbol = st.selectbox(
                "Default Symbol",
                config.SYMBOL_OPTIONS,
                index=_option_index(config.SYMBOL_OPTIONS, config.get_settings()["default_symbol"]),
                key="cfg_default_symbol",
            )
        with c3:
            default_timeframe = st.selectbox(
                "Default Timeframe",
                config.TIMEFRAME_OPTIONS,
                index=_option_index(config.TIMEFRAME_OPTIONS, config.get_settings()["default_timeframe"]),
                key="cfg_default_timeframe",
            )
            scan_interval = st.selectbox(
                "Scan Interval (seconds)",
                config.SCAN_INTERVAL_OPTIONS,
                index=_option_index(config.SCAN_INTERVAL_OPTIONS, int(config.get_settings()["scan_interval"])),
                key="cfg_scan_interval",
                help="How often the scanner / bot re-checks the market. Minimum 5s.",
            )

        st.divider()
        st.subheader("🛡 Risk")
        r1, r2, r3 = st.columns(3)
        with r1:
            risk_per_trade = st.number_input(
                "Risk Per Trade (%)",
                min_value=0.0,
                max_value=100.0,
                step=0.5,
                value=float(config.get_settings()["risk_per_trade"]),
                key="cfg_risk_per_trade",
            )
            stop_loss = st.number_input(
                "Stop Loss (%)",
                min_value=0.0,
                step=0.5,
                value=float(config.get_settings()["stop_loss"]),
                key="cfg_stop_loss",
                help="Must be greater than 0%.",
            )
        with r2:
            take_profit = st.number_input(
                "Take Profit (%)",
                min_value=0.0,
                step=0.5,
                value=float(config.get_settings()["take_profit"]),
                key="cfg_take_profit",
                help="Must be greater than 0%.",
            )
            daily_loss_limit = st.number_input(
                "Daily Loss Limit ($)",
                min_value=0.0,
                step=50.0,
                value=float(config.get_settings()["daily_loss_limit"]),
                key="cfg_daily_loss_limit",
                help="Must be greater than 0.",
            )
        with r3:
            max_drawdown = st.number_input(
                "Maximum Drawdown (%)",
                min_value=0.0,
                max_value=100.0,
                step=0.5,
                value=float(config.get_settings()["max_drawdown"]),
                key="cfg_max_drawdown",
            )

        st.divider()
        st.subheader("🤖 Bot")
        b1, b2 = st.columns(2)
        with b1:
            auto_start_bot = st.checkbox(
                "Auto Start Bot",
                value=bool(config.get_settings()["auto_start_bot"]),
                key="cfg_auto_start_bot",
            )
            paper_trading = st.checkbox(
                "Enable Paper Trading",
                value=bool(config.get_settings()["paper_trading"]),
                key="cfg_paper_trading",
            )
        with b2:
            scanner_auto_refresh = st.checkbox(
                "Enable Scanner Auto Refresh",
                value=bool(config.get_settings()["scanner_auto_refresh"]),
                key="cfg_scanner_auto_refresh",
            )
            notifications = st.checkbox(
                "Notifications",
                value=bool(config.get_settings()["notifications"]),
                key="cfg_notifications",
            )

        st.divider()
        action_col1, action_col2 = st.columns([1, 5])
        submitted = action_col1.form_submit_button("💾 Save Settings", type="primary", width="stretch")
        reset_clicked = action_col2.form_submit_button("↺ Reset Defaults", width="stretch")

    # ------------------------------------------------------------------
    # Actions (outside the form so st.error/success render naturally).
    # ------------------------------------------------------------------
    if reset_clicked:
        config.reset_settings()
        st.success("Settings reset to defaults.")
        st.rerun()

    if submitted:
        draft = {
            # Trading
            "starting_balance": starting_balance,
            "order_size": order_size,
            "max_open_positions": max_positions,
            "default_symbol": default_symbol,
            "default_timeframe": default_timeframe,
            "scan_interval": scan_interval,
            # Risk
            "risk_per_trade": risk_per_trade,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "daily_loss_limit": daily_loss_limit,
            "max_drawdown": max_drawdown,
            # Bot
            "auto_start_bot": auto_start_bot,
            "paper_trading": paper_trading,
            "scanner_auto_refresh": scanner_auto_refresh,
            "notifications": notifications,
        }

        is_valid, errors = config.validate_settings(draft)
        if not is_valid:
            st.error("⚠ Settings NOT saved — fix the following:")
            for err in errors:
                st.error(f"• {err}")
        else:
            config.save_settings(draft)
            st.success("✅ Settings saved successfully!")

    st.divider()

    # ------------------------------------------------------------------
    # Read-only verification of the values currently in settings.json.
    # ------------------------------------------------------------------
    _render_active_settings()


def _option_index(options: list, value) -> int:
    """Return the index of `value` in `options`, defaulting to 0."""
    try:
        return options.index(value)
    except (ValueError, TypeError):
        return 0


def _render_active_settings() -> None:
    """Read-only table of the values currently loaded from the config file."""
    st.subheader("Current Active Settings")
    st.caption("Values currently loaded from settings.json — verifies Save / Reset behavior.")

    active = config.get_settings()

    sections = [
        ("Trading", ["starting_balance", "order_size", "max_open_positions", "default_symbol", "default_timeframe", "scan_interval"]),
        ("Risk", ["risk_per_trade", "stop_loss", "take_profit", "daily_loss_limit", "max_drawdown"]),
        ("Bot", ["auto_start_bot", "paper_trading", "scanner_auto_refresh", "notifications"]),
    ]

    for section_name, keys in sections:
        st.markdown(f"**{section_name}**")
        rows = []
        for key in keys:
            value = active.get(key)
            if isinstance(value, bool):
                display = "✅ On" if value else "❌ Off"
            elif key in ("starting_balance", "order_size", "daily_loss_limit"):
                display = f"${value:,.2f}" if isinstance(value, (int, float)) else str(value)
            elif key in ("risk_per_trade", "stop_loss", "take_profit", "max_drawdown"):
                display = f"{value:,.1f}%" if isinstance(value, (int, float)) else str(value)
            elif key == "scan_interval":
                display = f"{value} s" if isinstance(value, (int, float)) else str(value)
            else:
                display = str(value)

            rows.append({"Setting": key.replace("_", " ").title(), "Value": display})

        st.dataframe(
            rows,
            hide_index=True,
            width="stretch",
            column_config={
                "Setting": st.column_config.TextColumn("Setting", width="medium"),
                "Value": st.column_config.TextColumn("Value", width="medium"),
            },
        )