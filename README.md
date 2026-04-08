# Canada National Fire Weather Dashboard

A lightweight situational awareness dashboard that with access to public data sources in a single dashboard.

This dashboard is intended to run on Windows with minimal permissions or installs required.

## Requirements

1. Windows Powershell with the ability to bypass the execution policy
2. Python 3.xx
3. A browser with ability to enable pop-ups. This is due to the javascript methods used to open new tabs being caught by some pop-up blocking.

## What it does

The dashboard gives one-click access to public data resources regarding current national weather/watches/warnings as well as pertinent news stories regarding fire or smoke. What it does versus a collection of bookmarks

1. Single dashboard view of national and regional weather forecast and agency fire weather pages
2. RSS feed of recent and pertinent news articles regarding fire or smoke, for situational awarness
3. Tweaked GOES IR composite with presets for longer loops and faster animation than the defaults on ECCC

## How to use

### Windows

Double-click:

- `start_briefing.bat`

To stop the background server and refresher later, double-click:

- `stop_briefing.bat`

The start launcher now hands off to `start_briefing.ps1`, which is more reliable for keeping the local Python server and news refresher running in the background on Windows.

You can also run either script directly from PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\start_briefing.ps1
powershell -ExecutionPolicy Bypass -File .\stop_briefing.ps1
```

> If `Open core sources` or `Open regional follow-up` only opens one tab in Edge, allow pop-ups for `127.0.0.1:8765` (or the local dashboard page) and try again. This has been confirmed to resolve the issue in Edge.

If the local Windows launch ever fails again, check these logs:

- `%TEMP%\fire-weather-briefing\server.out.log`
- `%TEMP%\fire-weather-briefing\server.err.log`
- `%TEMP%\fire-weather-briefing\rss_fetch.log`
- `%TEMP%\fire-weather-briefing\goes_fetch.log`

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
- `start_briefing.ps1` / `start_briefing.bat` — Windows launchers for the live local dashboard
- `stop_briefing.ps1` / `stop_briefing.bat` — Windows cleanup scripts to stop the background processes
- `data/news.json` — cached headline results used by the dashboard

## Maintenance

To change sources, edit `config/sources.json`.

When launched through `start_briefing.bat` or `start_briefing.sh`, the dashboard first refreshes recent wildfire-related headlines and regenerates the configured GOES page, then starts a lightweight background refresher that updates `data/news.json` every 30 minutes. The open dashboard polls that file on the same cadence.

The page also contains a built-in fallback source list so it still works when launched directly as a local file with no web server. In this case only static links will work, and the RSS feed will not load or update.

For security reasons, the dashboard page itself does not directly start or stop local scripts from within the browser. The external `start_briefing.*` and `stop_briefing.*` launchers are the simpler and more reliable approach.

