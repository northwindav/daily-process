/**
 * METAR Observation Viewer - Frontend JavaScript
 * Handles form submission, API requests, and result display
 */

let allStations = [];

/**
 * Initialize the page: load stations and set up event listeners
 */
async function init() {
  try {
    // Load station reference data
    const response = await fetch("../config/metar_stations.json");
    if (response.ok) {
      allStations = await response.json();
    } else {
      console.warn("Could not load station list");
    }
  } catch (error) {
    console.error("Error loading stations:", error);
  }

  // Populate station reference list
  populateStationList(allStations);

  // Initialize map
  initMap();

  // Set up event listeners
  document.getElementById("fetch-button").addEventListener("click", handleFetch);
  document.getElementById("clear-button").addEventListener("click", () => {
    document.getElementById("results-container").innerHTML = "";
    showStatus("");
  });
  document.getElementById("station-code").addEventListener("keypress", (e) => {
    if (e.key === "Enter") handleFetch();
  });

  document.getElementById("station-search").addEventListener("input", (e) => {
    const query = e.target.value.toLowerCase();
    const filtered = allStations.filter((station) => {
      const text = `${station.icao} ${station.iata} ${station.name} ${station.region} ${station.country}`.toLowerCase();
      return text.includes(query);
    });
    populateStationList(filtered);
  });
}

/**
 * Populate the station reference list
 */
function populateStationList(stations) {
  const container = document.getElementById("station-list");
  container.innerHTML = "";

  stations.forEach((station) => {
    const div = document.createElement("div");
    div.className = "station-item";
    div.innerHTML = `<strong>${station.icao}</strong> (${station.iata}) — ${station.name}<small>${station.region}</small>`;
    div.style.cursor = "pointer";

    div.addEventListener("click", () => {
      document.getElementById("station-code").value = station.icao;
      document.getElementById("station-code").focus();
    });

    container.appendChild(div);
  });

  if (stations.length === 0) {
    container.innerHTML = '<div style="padding: 1rem; color: #999; text-align: center;">No stations found</div>';
  }
}

/**
 * Initialize the map with OpenStreetMap tiles and station markers
 */
let mapInstance = null;
let stationMarkers = {};

function initMap() {
  // Create map centered on Canada
  mapInstance = L.map("map").setView([56, -95], 3);

  // Add OpenStreetMap tiles
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: '© OpenStreetMap contributors',
    maxZoom: 18,
  }).addTo(mapInstance);

  // Add markers for all stations
  allStations.forEach((station) => {
    const marker = L.marker([station.lat, station.lon])
      .bindPopup(`<strong>${station.icao}</strong><br/>${station.name}<br/>${station.region}`)
      .addTo(mapInstance);

    marker.on("click", () => {
      // When marker is clicked, populate the search box
      document.getElementById("station-code").value = station.icao;
      document.getElementById("station-code").focus();
    });

    stationMarkers[station.icao] = marker;
  });
}

/**
 * Handle fetch button click
 */
async function handleFetch() {
  const stationInput = document.getElementById("station-code").value.trim().toUpperCase();
  const hours = document.getElementById("hours-select").value;
  const timezone = document.getElementById("timezone-select").value;

  // Validate input
  if (!stationInput) {
    showStatus("Please enter a station code", "error");
    return;
  }

  if (stationInput.length !== 4) {
    showStatus("Station code must be 4 characters", "error");
    return;
  }

  showStatus("Loading observations...", "loading");

  try {
    // Call API
    const params = new URLSearchParams({
      stations: stationInput,
      hours: hours,
      tz: timezone,
    });

    const response = await fetch(`/api/metar?${params}`);
    const data = await response.json();

    if (!data.success) {
      showStatus(`Error: ${data.error}`, "error");
      return;
    }

    // Display results
    displayResults(data.data, timezone);
    showStatus(""); // Clear status
  } catch (error) {
    showStatus(`Network error: ${error.message}`, "error");
  }
}

/**
 * Display results in table format
 */
function displayResults(results, timezone) {
  const container = document.getElementById("results-container");
  container.innerHTML = "";

  if (!results || results.length === 0) {
    showStatus("No observations found for this station", "error");
    return;
  }

  results.forEach((station) => {
    const section = document.createElement("div");
    section.className = "metar-section";

    const header = document.createElement("div");
    header.className = "station-header";
    const latStr = station.lat ? station.lat.toFixed(3) : "—";
    const lonStr = station.lon ? station.lon.toFixed(3) : "—";
    const elevStr = station.elev ? `${station.elev}m` : "—";
    header.textContent = `${station.icao} — ${station.observations.length} observations | Lat ${latStr}, Lon ${lonStr}, Elev ${elevStr}`;

    const table = document.createElement("table");
    table.className = "metar-results";

    // Table header
    const thead = document.createElement("thead");
    const headerRow = document.createElement("tr");
    const columns = ["Time", "Temp (°C)", "Td (°C)", "RH (%)", "Wind (km/h)", "Vis (SM)", "SLP (hPa)", "Weather", "Sky", "Remarks"];

    columns.forEach((col) => {
      const th = document.createElement("th");
      th.textContent = col;
      headerRow.appendChild(th);
    });

    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Table body
    const tbody = document.createElement("tbody");

    // Sort observations by time (newest first)
    const sorted = [...station.observations].sort((a, b) => new Date(b.time) - new Date(a.time));

    sorted.forEach((obs) => {
      const row = document.createElement("tr");

      const cells = [
        obs.time,
        obs.temp_c !== null ? obs.temp_c.toFixed(1) : "—",
        obs.dewpoint_c !== null ? obs.dewpoint_c.toFixed(1) : "—",
        obs.rh_percent !== null ? obs.rh_percent.toFixed(0) : "—",
        obs.wind || "—",
        obs.visibility || "—",
        obs.pressure || "—",
        obs.weather || "—",
        obs.clouds || "—",
        obs.remarks || "—",
      ];

      cells.forEach((cell, index) => {
        const td = document.createElement("td");
        td.textContent = cell;
        
        // Highlight Temp (index 1) and RH (index 3) in red if RH <= T
        if ((index === 1 || index === 3) && obs.temp_c !== null && obs.rh_percent !== null) {
          if (obs.rh_percent <= obs.temp_c) {
            td.style.color = "red";
            td.style.fontWeight = "bold";
          }
        }
        
        row.appendChild(td);
      });

      tbody.appendChild(row);
    });

    table.appendChild(tbody);

    section.appendChild(header);
    section.appendChild(table);
    container.appendChild(section);
  });
}

/**
 * Show status message
 */
function showStatus(message, type = "") {
  const statusEl = document.getElementById("status-message");

  if (!message) {
    statusEl.style.display = "none";
    return;
  }

  statusEl.textContent = message;
  statusEl.className = "metar-status " + type;
  statusEl.style.display = "block";
}

// Initialize when DOM is ready
document.addEventListener("DOMContentLoaded", init);
