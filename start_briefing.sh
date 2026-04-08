#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT="${PORT:-8765}"
URL="http://127.0.0.1:${PORT}/dashboard/index.html"
LOCAL_FILE="${BASE_DIR}/dashboard/index.html"

if command -v python3 >/dev/null 2>&1; then
  (
    cd "${BASE_DIR}"
    python3 scripts/fetch_rss.py >/dev/null 2>&1 || true
    python3 scripts/fetch_goes_page.py >/dev/null 2>&1 || true
    nohup python3 scripts/refresh_news_loop.py >/dev/null 2>&1 &
    nohup python3 -m http.server "${PORT}" >/dev/null 2>&1 &
  )
  xdg-open "${URL}" >/dev/null 2>&1 || printf 'Open this URL in a browser: %s\n' "${URL}"
else
  xdg-open "${LOCAL_FILE}" >/dev/null 2>&1 || printf 'Open this file in a browser: %s\n' "${LOCAL_FILE}"
fi
