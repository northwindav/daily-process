# Canada Fire Weather Briefing MVP

This workspace contains a **dashboard-first MVP** for daily Canada-wide fire-weather situational awareness.

## What it does

The dashboard is designed to answer three questions quickly each morning:

1. What is the broad weather pattern across Canada?
2. What watches, warnings, or special weather statements are active?
3. What wildfire developments or major news items are notable right now?

## How to use

### Windows

Double-click:

- `start_briefing.bat`

> If `Open core sources` or `Open regional follow-up` only opens one tab in Edge, allow pop-ups for `127.0.0.1:8765` (or the local dashboard page) and try again. This has been confirmed to resolve the issue in Edge.

### Ubuntu

Run:

```bash
./start_briefing.sh
```

## Files

- `dashboard/index.html` — main dashboard page
- `dashboard/app.js` — renders source cards, buttons, and recent headlines
- `dashboard/styles.css` — dashboard styling
- `dashboard/goes_ir_configured.html` — generated GOES IR page tuned for the morning scan
- `config/sources.json` — curated list of source links and notes
- `scripts/fetch_rss.py` — refreshes wildfire-related headlines from the last 24 hours
- `scripts/fetch_goes_page.py` — regenerates the configured GOES IR page
- `scripts/refresh_news_loop.py` — lightweight 30-minute background news refresher
- `data/news.json` — cached headline results used by the dashboard

## Maintenance

To change sources, edit `config/sources.json`.

When launched through `start_briefing.bat` or `start_briefing.sh`, the dashboard first refreshes recent wildfire-related headlines and regenerates the configured GOES page, then starts a lightweight background refresher that updates `data/news.json` every 30 minutes. The open dashboard polls that file on the same cadence.

The page also contains a built-in fallback source list so it still works when launched directly as a local file with no web server.

## Suggested next steps

- Fine-tune the keyword list or add seasonal terms
- Add province/territory prioritization based on current activity
- Optionally upgrade to a lightweight `Streamlit` interface later
