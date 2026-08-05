import threading
import time
from datetime import datetime

from app.bot.trader import run_bot
from app.core.config import get_int

# Previous hardcoded scan interval (seconds) — used as the safe fallback
# when the setting is missing or invalid.
_DEFAULT_INTERVAL = 60

_running = False
_thread = None


def _timestamp() -> str:
    return datetime.now().strftime("%H:%M:%S")


def _worker():
    global _running

    print("🤖 Auto Trader Started")

    while _running:
        try:
            run_bot()
        except Exception as exc:
            print(f"[{_timestamp()}] ERROR Scheduler {exc}")

        # Read the configured scan interval on every tick so setting changes
        # are picked up naturally at runtime (fallback: previous default 60s).
        interval = get_int("scan_interval", _DEFAULT_INTERVAL, min_value=5)

        for _ in range(interval):
            if not _running:
                break
            time.sleep(1)

    print("🛑 Auto Trader Stopped")


def start_bot():
    global _running, _thread

    if _running:
        return

    _running = True

    _thread = threading.Thread(target=_worker, daemon=True)
    _thread.start()


def stop_bot():
    global _running

    _running = False


def is_running():
    return _running