# Canada National Fire Weather Dashboard

A lightweight situational awareness dashboard that with access to public data sources in a single dashboard.

This dashboard is intended to run on Windows with minimal permissions or installs required.

## Requirements

1. Windows Powershell with the ability to bypass the execution policy
2. Python 3.xx
3. A browser with ability to enable pop-ups. This is due to the javascript methods used to open new tabs being caught by some pop-up blocking.

## What it does

The dashboard gives one-click access to public data resources regarding current national weather, fire conditions, wildfire status, and pertinent news stories. Compared to a collection of bookmarks:

1. **Consolidated dashboard view** organized into five sections: National Overview (weather + CWFIS fire conditions), Wildfire status, News (with filtered RSS headlines from last 24 hours), and Regional follow-up
2. **Live RSS headline feed** displaying recent and pertinent wildfire-related news articles from multiple outlets (auto-refreshes every 30 minutes)
3. **Pre-configured GOES IR page** tuned for the morning scan with longer animation loops and faster playback than ECCC defaults
4. **METAR Observation Viewer** for quick access to current station observations across Canada and northern USA (1–48 hour history with timezone support)
5. **Multi-tab button workflows** to quickly open all core sources or regional follow-up sources at once

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
- `dashboard/metar.html` — METAR observation viewer page
- `dashboard/metar.js` — METAR form handler and results display
- `config/sources.json` — curated list of source links and notes
- `config/metar_stations.json` — reference list of METAR stations (74 total: 49 Canadian, 25 US north of 40°N)
- `scripts/fetch_rss.py` — refreshes wildfire-related headlines from the last 24 hours
- `scripts/fetch_goes_page.py` — regenerates the configured GOES IR page
- `scripts/refresh_news_loop.py` — lightweight 30-minute background news refresher
- `scripts/metar_handler.py` — METAR API handler for querying aviationweather.gov observations
- `scripts/server.py` — custom HTTP server with API routing for METAR endpoint
- `scripts/update_stations.py` — utility to refresh station list from aviationweather.gov (run 2-3x per year)
- `start_briefing.ps1` / `start_briefing.bat` — Windows launchers for the live local dashboard
- `stop_briefing.ps1` / `stop_briefing.bat` — Windows cleanup scripts to stop the background processes
- `data/news.json` — cached headline results used by the dashboard

## Dashboard structure

The dashboard is organized into five main sections, each rendered from the `sources` array in `config/sources.json`:

- **National Overview** — Weather patterns and fire conditions (GOES IR, AniMet weather analysis, CWFIS interactive map with FWI and active fires)
- **Wildfire status** — National fire activity (CIFFC maps and summaries, CWFIS federal products)
- **News in the last 24 hours** — Filtered RSS headlines followed by news source links (CBC, CTV, Global, The Weather Network, and wildfire-specific searches)
- **Regional follow-up** — Provincial and territorial wildfire and emergency resources (opened via the "Open regional follow-up" button)

Two quick-access buttons at the top:
- **Open core sources** — Opens all National Overview and Wildfire status sources in separate tabs
- **Open regional follow-up** — Opens all Regional resources in separate tabs

### METAR Observation Viewer

Accessible from the dashboard as a separate tab, the METAR viewer provides quick access to recent station observations:

- **Station search**: Enter a 4-character IATA or ICAO code (e.g., YYZ for Toronto, JFK for New York)
- **Time range**: Select 1, 6, 12, 24, or 48 hours back (default: 12 hours)
### METAR Observation Viewer

Accessible from the dashboard as a separate tab, the METAR viewer provides quick access to recent station observations:

- **Station search**: Enter a 4-character IATA or ICAO code (e.g., YYZ for Toronto, JFK for New York)
- **Time range**: Select 1, 6, 12, 24, or 48 hours back (default: 12 hours)
- **Timezone**: Choose UTC or 6 North American abbreviations (PDT, MDT, CDT, EDT, NDT) for time display
- **Results**: Displays observations in a table with:
  - Time, temperature, dew point, relative humidity (RH), wind, visibility, pressure, weather, cloud layers, and remarks
  - **Conditional highlighting**: Temperature and RH values display in bold red when RH ≤ T (useful for fire weather monitoring)
  - **Newest-first sort**: Most recent observations appear first for quick scanning
- **Station reference**: Searchable list of 74 weather stations (49 Canadian, 25 US north of 40°N) for quick lookups
- **Interactive map**: Zoomable OpenStreetMap display showing all available station locations with markers (click any marker to auto-populate the search box)

Data is queried on-demand from aviationweather.gov; no caching or history is retained. Station list updates 2-3 times per year via `scripts/update_stations.py`.

## Future enhancements

**Phase 2 (Planned)**: Expand METAR data to include partner stations from dd.weather.gc.ca, enabling access to additional Canadian surface observation networks (roadside stations, forestry sites, etc.) for more granular regional fire weather monitoring.

## Maintenance

To change sources or add/remove sections, edit `config/sources.json`. The dashboard reads and renders all sources dynamically based on their `category` field (weather, wildfire, news, regional).

To modify the dashboard structure itself, edit `dashboard/index.html` for layout and `dashboard/app.js` for rendering logic.

When launched through `start_briefing.bat` or `start_briefing.sh`:
1. The dashboard first refreshes recent wildfire-related headlines from configured RSS feeds
2. It regenerates the pre-configured GOES IR page
3. A lightweight 30-minute background refresher keeps `data/news.json` up-to-date
4. The open dashboard polls the news feed on the same 30-minute cadence

The dashboard also contains a built-in fallback source list so it still works when launched as a local file with no web server. In this case, only static links work and the live RSS feed will not load or update.

For security reasons, the dashboard page itself does not start or stop local background processes. The external `start_briefing.*` and `stop_briefing.*` launchers manage the Python server and news refresh loop.

## Current news sources

The dashboard automatically refreshes headlines from these outlets (via Google News RSS search):
- CBC News — National and specific wildfire searches
- CTV News — Global news feed
- Global News — National and specific wildfire searches  
- The Weather Network — Weather-focused news
- Google News — Wildfire-specific search across all outlets

## Third-party Libraries

This project includes the following open-source library:

- **gif.js** (MIT License) — Client-side JavaScript GIF encoder using Web Workers  
  https://github.com/jnordberg/gif.js  
  Copyright © 2013-2018 Johan Nordberg

For full license text, see: https://github.com/jnordberg/gif.js/blob/master/LICENSE

