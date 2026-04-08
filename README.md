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

### Ubuntu

Run:

```bash
./start_briefing.sh
```

## Files

- `dashboard/index.html` — main dashboard page
- `dashboard/app.js` — renders source cards, buttons, and recent headlines
- `dashboard/styles.css` — dashboard styling
- `config/sources.json` — curated list of source links and notes
- `scripts/fetch_rss.py` — refreshes wildfire-related headlines from the last 24 hours
- `data/news.json` — cached headline results used by the dashboard

## Maintenance

To change sources, edit `config/sources.json`.

When launched through `start_briefing.bat` or `start_briefing.sh`, the dashboard first refreshes recent wildfire-related headlines from CBC plus additional national news feeds and then opens the page.

The page also contains a built-in fallback source list so it still works when launched directly as a local file with no web server.

## Suggested next steps

- Fine-tune the keyword list or add seasonal terms
- Add province/territory prioritization based on current activity
- Optionally upgrade to a lightweight `Streamlit` interface later
