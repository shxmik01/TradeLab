import threading
import time
from datetime import datetime

from app.bot.trader import run_bot

INTERVAL = 60

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

        for _ in range(INTERVAL):
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