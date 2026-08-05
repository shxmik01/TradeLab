"""Central configuration module for the crypto paper bot.

All application settings live in a single JSON file (`settings.json` in the
project root, next to `wallet.db`). This module is the single source of truth:

- `DEFAULT_SETTINGS`   — canonical defaults (the UI options are derived from these)
- `load_settings()`    — read + merge the JSON file with defaults
- `save_settings()`    — atomic write back to disk
- `reset_settings()`   — restore the defaults on disk
- `get_settings()`     — cached accessor other modules can import immediately
- `validate_settings()`— per-field validation (min/max/positive) with human errors

Future modules (e.g. PaperWallet, Scheduler, Strategy) can replace their
hardcoded values by importing `get_settings()` — no architecture change needed.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parents[2]
SETTINGS_PATH = BASE_DIR / "settings.json"

# ---------------------------------------------------------------------------
# Canonical defaults — every editable value in the Settings page lives here.
# ---------------------------------------------------------------------------
DEFAULT_SETTINGS: dict[str, Any] = {
    # Trading
    "starting_balance": 10000.0,
    "order_size": 250.0,
    "max_open_positions": 4,
    "default_symbol": "BTCUSDT",
    "default_timeframe": "1h",
    "scan_interval": 60,
    # Risk
    "risk_per_trade": 2.0,
    "stop_loss": 5.0,
    "take_profit": 10.0,
    "daily_loss_limit": 500.0,
    "max_drawdown": 20.0,
    # Bot
    "auto_start_bot": False,
    "paper_trading": True,
    "scanner_auto_refresh": True,
    "notifications": True,
}

# Option lists used by the UI — derived from canonical data, not hardcoded
# in the page itself. Edit these in one place only.
SYMBOL_OPTIONS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT"]
TIMEFRAME_OPTIONS = ["1m", "5m", "15m", "1h", "4h", "1d"]
SCAN_INTERVAL_OPTIONS = [5, 10, 15, 30, 60, 120, 300, 600]

# Validation bounds shared by validate_settings().
_BOUNDS: dict[str, dict[str, float | None]] = {
    "starting_balance": {"min": 0.0, "min_exclusive": True, "label": "Starting Balance"},
    "order_size": {"min": 0.0, "min_exclusive": True, "label": "Default Order Size"},
    "max_open_positions": {"min": 1, "min_exclusive": False, "label": "Max Open Positions"},
    "scan_interval": {"min": 5, "min_exclusive": False, "label": "Scan Interval"},
    "risk_per_trade": {"min": 0.0, "max": 100.0, "label": "Risk Per Trade"},
    "stop_loss": {"min": 0.0, "min_exclusive": True, "label": "Stop Loss"},
    "take_profit": {"min": 0.0, "min_exclusive": True, "label": "Take Profit"},
    "daily_loss_limit": {"min": 0.0, "min_exclusive": True, "label": "Daily Loss Limit"},
    "max_drawdown": {"min": 0.0, "max": 100.0, "label": "Maximum Drawdown"},
}

_cached_settings: dict[str, Any] | None = None


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------
def load_settings() -> dict[str, Any]:
    """Load settings from disk, merged over the defaults.

    Creates `settings.json` with defaults on first run. Unknown keys in the
    file are preserved, and any missing default keys are back-filled, so the
    file can never crash the rest of the app.
    """
    global _cached_settings

    data: dict[str, Any] = {}
    if SETTINGS_PATH.exists():
        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as fh:
                parsed = json.load(fh)
            if isinstance(parsed, dict):
                data = parsed
        except (json.JSONDecodeError, OSError):
            # Corrupt/unreadable file — fall back to defaults; the next save
            # will rewrite the file cleanly.
            data = {}

    # Merge: defaults provide structure, file provides overrides.
    merged = {**DEFAULT_SETTINGS, **{k: v for k, v in data.items() if k in DEFAULT_SETTINGS}}

    if not SETTINGS_PATH.exists():
        _write(merged)

    _cached_settings = dict(merged)
    return dict(merged)


def save_settings(settings: dict[str, Any]) -> dict[str, Any]:
    """Persist `settings` to the JSON file atomically and refresh the cache."""
    global _cached_settings

    # Coerce the numeric fields so the JSON file stays clean.
    clean = _coerce_types(settings)
    _write(clean)
    _cached_settings = dict(clean)
    return dict(clean)


def reset_settings() -> dict[str, Any]:
    """Restore the canonical defaults both on disk and in the cache."""
    global _cached_settings

    _write(dict(DEFAULT_SETTINGS))
    _cached_settings = dict(DEFAULT_SETTINGS)
    return dict(DEFAULT_SETTINGS)


def get_settings() -> dict[str, Any]:
    """Return the current in-memory settings (cached copy of the JSON file).

    Other modules should call `get_settings()` in their hot path — e.g.

        from app.core.config import get_settings
        cfg = get_settings()
        position_size = cfg["order_size"]           # default 250.0
        max_positions = cfg["max_open_positions"]   # default 4

    and replace their hardcoded constants with these values. The cache is
    only refreshed by `load_settings()` / `save_settings()` / `reset_settings()`.
    """
    if _cached_settings is None:
        return load_settings()
    return dict(_cached_settings)


def get_float(
    key: str,
    default: float,
    min_value: float | None = None,
    min_exclusive: bool = False,
) -> float:
    """Return a validated numeric setting, falling back to `default`.

    Used by runtime components to replace hardcoded constants. If the stored
    value is missing from the raw file, non-numeric, or violates the bound,
    the previous hardcoded default is returned so behavior is preserved.
    """
    raw = _raw_value(key)
    if raw is None:
        return default

    try:
        value = float(raw) if isinstance(raw, (int, float)) else float(str(raw))
    except (TypeError, ValueError):
        return default

    if min_value is not None:
        if min_exclusive and value <= float(min_value):
            return default
        if not min_exclusive and value < float(min_value):
            return default

    return value


def get_int(key: str, default: int, min_value: int | None = None) -> int:
    """Return a validated integer setting, falling back to `default`.

    Used by runtime components to replace hardcoded constants. Returns the
    nearest whole number; if the stored value is missing from the raw file,
    non-numeric, or below `min_value`, the previous hardcoded default is
    returned.
    """
    raw = _raw_value(key)
    if raw is None:
        return default

    try:
        value = int(round(float(raw) if isinstance(raw, (int, float)) else float(str(raw))))
    except (TypeError, ValueError):
        return default

    if min_value is not None and value < int(min_value):
        return default

    return value


def get_choice(key: str, default: str, options: list[str]) -> str:
    """Return a validated string setting from a canonical option list.

    Used by runtime components to replace hardcoded constants. Falls back to
    `default` when the stored value is missing from the raw file or not in
    `options`.
    """
    raw = _raw_value(key)
    if raw is None:
        return default

    try:
        value_str = str(raw)
    except (TypeError, ValueError):
        return default

    return value_str if value_str in options else default


def _raw_value(key: str) -> Any:
    """Return the raw value of `key` from the settings file, or None if the
    key is absent (or the file is unreadable).

    The in-memory cache always merges `DEFAULT_SETTINGS`, so it cannot
    distinguish a genuinely-absent key from one that was back-filled.
    Runtime getters check the raw file so a missing key reliably falls back
    to the caller's previous hardcoded default.
    """
    data: dict[str, Any] = {}
    if SETTINGS_PATH.exists():
        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as fh:
                parsed = json.load(fh)
            if isinstance(parsed, dict):
                data = parsed
        except (json.JSONDecodeError, OSError):
            return None

    if key not in data:
        return None
    return data[key]


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
def validate_settings(settings: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate a settings dict against the canonical bounds.

    Returns `(is_valid, human_readable_errors)`. The page calls this before
    saving; on failure nothing is persisted and the errors are displayed.
    """
    errors: list[str] = []

    for field, bounds in _BOUNDS.items():
        label: str = bounds["label"]  # type: ignore[assignment]
        raw = settings.get(field)

        try:
            value = float(raw) if isinstance(raw, (int, float)) else float(str(raw))
        except (TypeError, ValueError):
            errors.append(f"{label} must be a valid number")
            continue

        min_bound = bounds.get("min")
        max_bound = bounds.get("max")
        min_exclusive = bool(bounds.get("min_exclusive", False))

        if min_bound is not None:
            if min_exclusive:
                if value <= float(min_bound):
                    errors.append(f"{label} must be greater than {min_bound:g}")
            elif value < float(min_bound):
                errors.append(f"{label} must be at least {min_bound:g}")

        if max_bound is not None and value > float(max_bound):
            errors.append(f"{label} must be at most {max_bound:g}")

    # Enum-like string fields.
    symbol = str(settings.get("default_symbol", ""))
    if symbol not in SYMBOL_OPTIONS:
        errors.append("Default Symbol must be one of " + ", ".join(SYMBOL_OPTIONS))

    timeframe = str(settings.get("default_timeframe", ""))
    if timeframe not in TIMEFRAME_OPTIONS:
        errors.append("Default Timeframe must be one of " + ", ".join(TIMEFRAME_OPTIONS))

    if scan_interval := settings.get("scan_interval"):
        try:
            if int(scan_interval) not in SCAN_INTERVAL_OPTIONS:
                errors.append("Scan Interval must be one of " + ", ".join(str(x) for x in SCAN_INTERVAL_OPTIONS))
        except (TypeError, ValueError):
            errors.append("Scan Interval must be a valid number")

    return (not errors, errors)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
def _coerce_types(settings: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of `settings` with values typed like the defaults."""
    coerced = dict(settings)
    for key, default in DEFAULT_SETTINGS.items():
        if key not in coerced:
            coerced[key] = default
            continue
        if isinstance(default, bool):
            coerced[key] = bool(coerced[key])
        elif isinstance(default, int):
            try:
                coerced[key] = int(coerced[key])
            except (TypeError, ValueError):
                pass
        elif isinstance(default, float):
            try:
                coerced[key] = float(coerced[key])
            except (TypeError, ValueError):
                pass
        else:
            coerced[key] = str(coerced[key])
    return coerced


def _write(settings: dict[str, Any]) -> None:
    """Atomically write settings to disk (temp file + rename)."""
    temp_path = SETTINGS_PATH.with_suffix(".json.tmp")
    with open(temp_path, "w", encoding="utf-8") as fh:
        json.dump(settings, fh, indent=2)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(temp_path, SETTINGS_PATH)