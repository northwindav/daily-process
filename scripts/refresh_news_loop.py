from __future__ import annotations

import atexit
import json
import os
import signal
import time
from datetime import datetime, timezone
from pathlib import Path

from fetch_rss import main as refresh_news

INTERVAL_SECONDS = 30 * 60
BASE_DIR = Path(__file__).resolve().parents[1]
LOCK_PATH = BASE_DIR / "data" / "news_refresh.lock"


def process_is_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def release_lock() -> None:
    try:
        if not LOCK_PATH.exists():
            return

        data = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
        if data.get("pid") == os.getpid():
            LOCK_PATH.unlink()
    except Exception:
        pass


def acquire_lock() -> bool:
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)

    if LOCK_PATH.exists():
        try:
            data = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
            pid = int(data.get("pid", 0))
            if pid and process_is_running(pid):
                print(f"News refresh loop already running with PID {pid}.")
                return False
        except Exception:
            pass

        try:
            LOCK_PATH.unlink()
        except OSError:
            pass

    LOCK_PATH.write_text(
        json.dumps(
            {
                "pid": os.getpid(),
                "startedAt": datetime.now(timezone.utc).isoformat(),
                "intervalMinutes": INTERVAL_SECONDS // 60,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return True


def handle_exit(_signum=None, _frame=None) -> None:
    release_lock()
    raise SystemExit(0)


def main() -> None:
    if not acquire_lock():
        return

    atexit.register(release_lock)

    for signal_name in ("SIGINT", "SIGTERM", "SIGHUP"):
        if hasattr(signal, signal_name):
            signal.signal(getattr(signal, signal_name), handle_exit)

    print(f"Starting news refresh loop every {INTERVAL_SECONDS // 60} minutes.")

    try:
        refresh_news()
        while True:
            time.sleep(INTERVAL_SECONDS)
            refresh_news()
    finally:
        release_lock()


if __name__ == "__main__":
    main()
