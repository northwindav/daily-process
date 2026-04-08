const FALLBACK_DATA = {
  morningChecklist: [
    "Scan the national weather overview first to orient to the broad synoptic and fire-weather pattern.",
    "Check official Environment Canada warnings and statements for any active hazard signals.",
    "Review CIFFC and CWFIS for the national wildfire picture before drilling into any province or territory.",
    "Skim recent news for evacuations, smoke impacts, notable new fires, and major public messaging changes."
  ],
  sources: [
    {
      id: "goes-ir-composite",
      category: "weather",
      group: "core",
      region: "North America",
      label: "GOES IR composite",
      url: "goes_ir_configured.html",
      description: "Configured GOES IR loop showing roughly the last 3 hours at a faster animation speed.",
      why: "Fast first-look satellite view for Canada and surrounding upstream weather, pre-tuned for morning scanning."
    },
    {
      id: "animet-rdpa-alerts-lightning",
      category: "weather",
      group: "core",
      region: "Canada",
      label: "AniMet — RDPA, alerts, lightning, current conditions",
      url: "https://eccc-msc.github.io/msc-animet/?layers=HRDPA_2.5km_Precip-Accum24h-T12Z;0.75;0;1;0;1,CURRENT_CONDITIONS;0.75;0;1;0;1,Current-Alerts;0.75;0;1;0;1,Lightning_2.5km_Density;0.75;0;1;0;1,METNOTES;0.75;0;1;0;1&extent=-22549358,939440,2511850,13784292&overlays=Boundaries&range=30,l,l,PT24H",
      description: "AniMet blend of 24-hour precipitation, current conditions, alerts, lightning density, and met notes.",
      why: "Excellent all-in-one operational overview for active weather and fire-weather context."
    },
    {
      id: "animet-500hpa-thickness-precip",
      category: "weather",
      group: "core",
      region: "Canada",
      label: "AniMet — 500 hPa height, thickness, 3h precip",
      url: "https://eccc-msc.github.io/msc-animet/?layers=GDPS.PRES_GZ.500-CONTOUR;0.75;0;1;0;1,GDPS.ETA_DZ-CONTOUR;0.75;0;1;0;1,GDPS.DIAG_PR_PT3H;0.75;0;1;0;1&extent=-22549358,939440,2511850,13784292&overlays=Boundaries&range=80,2,l,PT3H",
      description: "AniMet synoptic setup with 500 hPa height, 1000–500 hPa thickness, and 3-hour precipitation.",
      why: "Useful for quickly interpreting the larger-scale pattern driving Canadian fire weather."
    },
    {
      id: "animet-pm25-smoke",
      category: "weather",
      group: "core",
      region: "Canada",
      label: "AniMet — total column PM2.5",
      url: "https://eccc-msc.github.io/msc-animet/?layers=RAQDPS.EAtm_PM2.5-WildfireSmokePlume;0.75;0;1;0;1&extent=-22549358,939440,2511850,13784292&overlays=Boundaries&range=72,7,l,PT1H",
      description: "AniMet smoke plume view using total column PM2.5 from RAQDPS wildfire smoke products.",
      why: "Adds a fast smoke-transport perspective to the national morning briefing."
    },
    {
      id: "ec-alerts",
      category: "alerts",
      group: "core",
      region: "Canada",
      label: "Environment Canada — weather homepage",
      url: "https://weather.gc.ca/index_e.html",
      description: "Environment Canada weather homepage with alerts, forecasts, and national access points.",
      why: "Reliable national entry point for hazard checks and follow-up navigation."
    },
    {
      id: "ciffc-map",
      category: "wildfire",
      group: "core",
      region: "Canada",
      label: "CIFFC — active fires map",
      url: "https://ciffc.net/",
      description: "National wildfire map, preparedness level, and headline activity indicators.",
      why: "Fastest wildfire snapshot across Canada."
    },
    {
      id: "ciffc-summary",
      category: "wildfire",
      group: "core",
      region: "Canada",
      label: "CIFFC — current fires summary",
      url: "https://ciffc.net/summary",
      description: "Current summary of national fire activity and control status.",
      why: "Useful for confirming what changed beyond the map view."
    },
    {
      id: "ciffc-sitrep",
      category: "wildfire",
      group: "core",
      region: "Canada",
      label: "CIFFC — situation reports",
      url: "https://ciffc.net/situation/archive",
      description: "Narrative context on the national fire situation.",
      why: "Adds concise written context to the national numbers."
    },
    {
      id: "cwfis-home",
      category: "wildfire",
      group: "core",
      region: "Canada",
      label: "CWFIS — national wildfire information",
      url: "https://cwfis.cfs.nrcan.gc.ca/en",
      description: "Federal wildfire information hub and related map products.",
      why: "Complements CIFFC with federal wildfire products."
    },
    {
      id: "cbc-canada",
      category: "news",
      group: "core",
      region: "Canada",
      label: "CBC News — Canada",
      url: "https://www.cbc.ca/news/canada",
      feedUrl: "https://www.cbc.ca/webfeed/rss/rss-canada",
      description: "National reporting that often captures major wildfire impacts and evacuations.",
      why: "Good first news skim for notable developments in the last 24 hours."
    },
    {
      id: "cbc-north",
      category: "news",
      group: "core",
      region: "North",
      label: "CBC News — North",
      url: "https://www.cbc.ca/news/canada/north",
      feedUrl: "https://www.cbc.ca/webfeed/rss/rss-canada-north",
      description: "Regional northern reporting where wildfire impacts can be significant.",
      why: "Helps surface stories that may be underrepresented in national feeds."
    },
    {
      id: "ctv-canada",
      category: "news",
      group: "core",
      region: "Canada",
      label: "CTV News — Canada",
      url: "https://www.ctvnews.ca/canada",
      feedUrl: "https://news.google.com/rss/search?q=wildfire+site%3Actvnews.ca&hl=en-CA&gl=CA&ceid=CA%3Aen",
      description: "National CTV coverage with a wildfire-focused RSS search feed.",
      why: "Adds a second national newsroom to the 24-hour wildfire scan."
    },
    {
      id: "global-canada",
      category: "news",
      group: "core",
      region: "Canada",
      label: "Global News — Canada",
      url: "https://globalnews.ca/canada/",
      feedUrl: "https://news.google.com/rss/search?q=wildfire+site%3Aglobalnews.ca&hl=en-CA&gl=CA&ceid=CA%3Aen",
      description: "National Global coverage with a wildfire-focused RSS search feed.",
      why: "Broadens the headline scan beyond CBC alone."
    },
    {
      id: "twn-news",
      category: "news",
      group: "core",
      region: "Canada",
      label: "The Weather Network — news",
      url: "https://www.theweathernetwork.com/en/news",
      feedUrl: "https://news.google.com/rss/search?q=wildfire+site%3Atheweathernetwork.com&hl=en-CA&gl=CA&ceid=CA%3Aen",
      description: "Weather-focused reporting with a wildfire-specific RSS search feed.",
      why: "Adds a weather-centric media lens to the daily news check."
    },
    {
      id: "cbc-search",
      category: "news",
      group: "core",
      region: "Canada",
      label: "CBC search — wildfire",
      url: "https://www.cbc.ca/search?q=wildfire",
      description: "Quick keyword search for recent wildfire-related stories.",
      why: "Efficient for identifying notable events from the previous day."
    },
    {
      id: "bc-wildfire",
      category: "regional",
      group: "regional",
      region: "British Columbia",
      label: "BC Wildfire Service",
      url: "https://wildfiresituation.nrs.gov.bc.ca/",
      description: "Provincial incident map and status information.",
      why: "Follow up here when BC appears active in the national picture."
    },
    {
      id: "ab-wildfire",
      category: "regional",
      group: "regional",
      region: "Alberta",
      label: "Alberta wildfire status",
      url: "https://www.alberta.ca/wildfire-status",
      description: "Alberta wildfire status and public updates.",
      why: "Useful regional follow-up during Prairie fire-weather events."
    },
    {
      id: "sk-incidents",
      category: "regional",
      group: "regional",
      region: "Saskatchewan",
      label: "Saskatchewan active incidents",
      url: "https://www.saskpublicsafety.ca/emergencies-and-response/active-incidents",
      description: "Active incidents and emergency context for Saskatchewan.",
      why: "Adds provincial follow-up when Saskatchewan is nationally significant."
    },
    {
      id: "mb-fireview",
      category: "regional",
      group: "regional",
      region: "Manitoba",
      label: "Manitoba FireView",
      url: "https://www.gov.mb.ca/conservation_fire/Fire-Maps/fireview/fireview_map.html",
      description: "Manitoba fire map and status view.",
      why: "Useful when Manitoba stands out in the national fire summary."
    },
    {
      id: "on-forest-fires",
      category: "regional",
      group: "regional",
      region: "Ontario",
      label: "Ontario forest fires",
      url: "https://www.ontario.ca/page/forest-fires",
      description: "Ontario public forest fire information.",
      why: "Provides provincial context beyond the national map."
    },
    {
      id: "qc-sopfeu",
      category: "regional",
      group: "regional",
      region: "Quebec",
      label: "SOPFEU",
      url: "https://www.sopfeu.qc.ca/",
      description: "Québec wildfire information and updates.",
      why: "Useful follow-up when eastern Canada becomes more active."
    },
    {
      id: "nt-fire",
      category: "regional",
      group: "regional",
      region: "Northwest Territories",
      label: "NWT Fire",
      url: "https://www.nwtfire.com/",
      description: "Northwest Territories wildfire status and updates.",
      why: "Important for northern wildfire situational awareness."
    },
    {
      id: "yukon-wildland-fires",
      category: "regional",
      group: "regional",
      region: "Yukon",
      label: "Yukon wildland fires",
      url: "https://yukon.ca/en/emergencies-and-safety/wildland-fires",
      description: "Yukon wildfire information and public guidance.",
      why: "Useful northern follow-up when the national picture points to Yukon."
    }
  ]
};

const EMPTY_NEWS_DATA = {
  generatedAt: null,
  keywords: [],
  itemCount: 0,
  errors: [],
  items: []
};

async function loadData() {
  if (window.location.protocol === "file:") {
    return { ...FALLBACK_DATA, loadedFrom: "fallback" };
  }

  try {
    const response = await fetch("../config/sources.json", { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const data = await response.json();
    return { ...data, loadedFrom: "json" };
  } catch (error) {
    console.warn("Falling back to embedded source list:", error);
    return { ...FALLBACK_DATA, loadedFrom: "fallback" };
  }
}

async function loadHeadlines() {
  if (window.location.protocol === "file:") {
    return { ...EMPTY_NEWS_DATA, loadedFrom: "file" };
  }

  try {
    const response = await fetch("../data/news.json", { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const data = await response.json();
    return { ...EMPTY_NEWS_DATA, ...data, loadedFrom: "json" };
  } catch (error) {
    console.warn("No cached news summary available yet:", error);
    return { ...EMPTY_NEWS_DATA, loadedFrom: "missing", error: String(error) };
  }
}

function renderChecklist(items) {
  const list = document.getElementById("checklist");
  list.innerHTML = "";

  items.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    list.appendChild(li);
  });
}

function renderCategory(sources, category, containerId) {
  const container = document.getElementById(containerId);
  container.innerHTML = "";

  const selected = sources.filter((source) => source.category === category);

  selected.forEach((source) => {
    const card = document.createElement("article");
    card.className = `source-card ${source.category}`;
    card.innerHTML = `
      <div class="card-meta">
        <span class="badge badge-category">${labelForCategory(source.category)}</span>
        <span class="badge badge-region">${source.region}</span>
      </div>
      <h3>${source.label}</h3>
      <p>${source.description}</p>
      <p class="why"><strong>Why this matters:</strong> ${source.why}</p>
      <div class="card-actions">
        <a class="btn-link" href="${source.url}" target="_blank" rel="noreferrer">Open source</a>
      </div>
    `;
    container.appendChild(card);
  });
}

function labelForCategory(category) {
  return {
    weather: "Weather",
    alerts: "Alerts",
    wildfire: "Wildfire",
    news: "News",
    regional: "Regional"
  }[category] || "Source";
}

function updateCounts(sources) {
  const counts = {
    weather: sources.filter((item) => item.category === "weather").length,
    alerts: sources.filter((item) => item.category === "alerts").length,
    wildfire: sources.filter((item) => item.category === "wildfire").length,
    news: sources.filter((item) => item.category === "news").length
  };

  document.getElementById("weather-count").textContent = counts.weather;
  document.getElementById("alerts-count").textContent = counts.alerts;
  document.getElementById("wildfire-count").textContent = counts.wildfire;
  document.getElementById("news-count").textContent = counts.news;
}

function openSources(sources, predicate) {
  const selected = sources.filter(predicate);

  selected.forEach((source, index) => {
    window.setTimeout(() => {
      window.open(source.url, "_blank", "noopener,noreferrer");
    }, index * 80);
  });
}

function setupButtons(sources) {
  document.getElementById("open-core").addEventListener("click", () =>
    openSources(sources, (source) => source.category === "weather")
  );

  document.getElementById("open-regional").addEventListener("click", () =>
    openSources(sources, (source) => source.group === "regional")
  );
}

function updateStatus(data) {
  const status = document.getElementById("data-status");
  status.textContent =
    data.loadedFrom === "json"
      ? "Loaded source list from config/sources.json"
      : "Using built-in source list for direct local-file launch";

  document.getElementById("generated-at").textContent = new Date().toLocaleString();
}

function formatPublishedDate(value) {
  if (!value) {
    return "Time unavailable";
  }

  const timestamp = new Date(value);
  if (Number.isNaN(timestamp.getTime())) {
    return "Time unavailable";
  }

  return timestamp.toLocaleString();
}

function getTimeAgeClass(value) {
  if (!value) {
    return "unknown";
  }

  const timestamp = new Date(value);
  if (Number.isNaN(timestamp.getTime())) {
    return "unknown";
  }

  const diffMinutes = Math.max(0, Math.round((Date.now() - timestamp.getTime()) / 60000));

  if (diffMinutes <= 180) {
    return "fresh";
  }

  if (diffMinutes <= 720) {
    return "recent";
  }

  return "older";
}

function formatRelativeTime(value) {
  if (!value) {
    return "Time unavailable";
  }

  const timestamp = new Date(value);
  if (Number.isNaN(timestamp.getTime())) {
    return "Time unavailable";
  }

  const diffMinutes = Math.max(0, Math.round((Date.now() - timestamp.getTime()) / 60000));

  if (diffMinutes < 60) {
    return `${diffMinutes} min ago`;
  }

  const diffHours = Math.round(diffMinutes / 60);
  if (diffHours < 24) {
    return `${diffHours}h ago`;
  }

  const diffDays = Math.round(diffHours / 24);
  return `${diffDays}d ago`;
}

function getSourceBadgeClass(sourceName) {
  const normalized = (sourceName || "").toLowerCase();

  if (normalized.includes("cbc")) {
    return "source-cbc";
  }

  if (normalized.includes("ctv")) {
    return "source-ctv";
  }

  if (normalized.includes("global")) {
    return "source-global";
  }

  if (normalized.includes("weather")) {
    return "source-weather";
  }

  return "";
}

function stripHtml(value) {
  const temp = document.createElement("div");
  temp.innerHTML = value || "";
  return (temp.textContent || temp.innerText || "").trim();
}

function renderHeadlines(newsData) {
  const status = document.getElementById("headlines-status");
  const meta = document.getElementById("news-meta");
  const list = document.getElementById("headline-list");

  if (!status || !meta || !list) {
    return;
  }

  list.innerHTML = "";

  const items = [...(newsData.items || [])]
    .sort((left, right) => new Date(right.published || 0).getTime() - new Date(left.published || 0).getTime())
    .slice(0, 12);

  if (newsData.loadedFrom === "json" && newsData.generatedAt) {
    meta.textContent = `Last RSS refresh: ${new Date(newsData.generatedAt).toLocaleString()}`;
  } else if (newsData.loadedFrom === "file") {
    meta.textContent = "Live headlines appear when you launch the dashboard through the one-click script.";
  } else {
    meta.textContent = "No cached headline file yet. Launch the dashboard again to refresh RSS headlines.";
  }

  const errorSuffix = newsData.errors?.length ? ` ${newsData.errors.length} feed refresh issue(s) occurred.` : "";

  if (!items.length) {
    status.textContent =
      newsData.loadedFrom === "json"
        ? `No wildfire-related headlines matched the current filters in the last 24 hours.${errorSuffix}`
        : "No cached wildfire headlines are available yet. Launch through the one-click script to build them.";
    return;
  }

  status.textContent = `Showing ${items.length} wildfire-related headline${items.length === 1 ? "" : "s"} from the last 24 hours.${errorSuffix}`;

  items.forEach((item) => {
    const ageClass = getTimeAgeClass(item.published);

    const li = document.createElement("li");
    li.className = `headline-item ${ageClass}`;

    const link = document.createElement("a");
    link.className = "headline-link";
    link.href = item.link || "#";
    link.target = "_blank";
    link.rel = "noreferrer";
    link.textContent = item.title || "Untitled headline";

    const metaRow = document.createElement("div");
    metaRow.className = "headline-meta";

    const source = document.createElement("span");
    source.className = `meta-badge source-badge ${getSourceBadgeClass(item.source)}`.trim();
    source.textContent = item.source || "News source";

    const published = document.createElement("span");
    published.className = `meta-badge time-badge ${ageClass}`;
    published.textContent = formatRelativeTime(item.published);
    published.title = formatPublishedDate(item.published);

    metaRow.append(source, published);
    li.append(link, metaRow);

    const description = stripHtml(item.description);
    if (description) {
      const descriptionNode = document.createElement("p");
      descriptionNode.textContent = description;
      li.appendChild(descriptionNode);
    }

    list.appendChild(li);
  });
}

window.addEventListener("DOMContentLoaded", async () => {
  const data = await loadData();
  const headlines = await loadHeadlines();

  renderChecklist(data.morningChecklist || FALLBACK_DATA.morningChecklist);
  renderCategory(data.sources, "weather", "weather-sources");
  renderCategory(data.sources, "alerts", "alerts-sources");
  renderCategory(data.sources, "wildfire", "wildfire-sources");
  renderCategory(data.sources, "news", "news-sources");
  renderCategory(data.sources, "regional", "regional-sources");
  renderHeadlines(headlines);
  updateCounts(data.sources);
  setupButtons(data.sources);
  updateStatus(data);
});
