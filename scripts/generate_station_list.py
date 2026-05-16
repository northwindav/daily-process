"""
Generate comprehensive metar_stations.json from MSC GeoMet SWOB collections and aviationweather.gov.

Purpose:
  Build a full station list with all available identifiers (ICAO, IATA, WMO, MSC ID, etc.)
  to enable empirical discovery of observation query syntax and field availability patterns.

Output:
  config/metar_stations.json with structure:
  {
    "code": "CYUL",
    "identifiers": { "icao", "iata", "wmo", "msc_id", "feature_id", "name" },
    "location": { "lat", "lon", "elevation_m" },
    "sources_available": ["geomet-swob-stations", "avwx"],
    "station_type": "airport" | "marine",
    "data_provider": "MSC" | "aviationweather.gov",
    ...
  }
"""

import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from typing import Dict, List, Optional

# Configuration
GEOMET_BASE_URL = "https://api.weather.gc.ca"
AVIATIONWEATHER_BASE_URL = "https://aviationweather.gov/api/data/metar"
API_TIMEOUT = 10
PAGE_SIZE = 500  # Geomet pagination limit
USER_AGENT = "fire-weather-briefing/1.0"

# Collections to fetch
SWOB_COLLECTIONS = ["swob-stations", "swob-partner-stations", "swob-marine-stations"]


def fetch_json(url: str, timeout: int = API_TIMEOUT) -> dict | None:
    """Fetch and parse JSON from URL."""
    try:
        req = urllib.request.Request(url)
        req.add_header("User-Agent", USER_AGENT)
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = response.read()
            return json.loads(data)
    except Exception as e:
        print(f"ERROR fetching {url}: {e}", file=sys.stderr)
        return None


def fetch_swob_stations() -> Dict[str, dict]:
    """Fetch all stations from SWOB collections with pagination."""
    stations = {}
    
    for collection in SWOB_COLLECTIONS:
        print(f"Fetching {collection}...", file=sys.stderr)
        offset = 0
        page_num = 0
        
        while True:
            page_num += 1
            url = f"{GEOMET_BASE_URL}/collections/{collection}/items?limit={PAGE_SIZE}&offset={offset}&f=json"
            
            print(f"  Page {page_num} (offset {offset})...", file=sys.stderr)
            data = fetch_json(url)
            
            if not data or "features" not in data:
                print(f"  No features found at offset {offset}. Stopping collection.", file=sys.stderr)
                break
            
            features = data["features"]
            if not features:
                print(f"  Empty page at offset {offset}. Done with {collection}.", file=sys.stderr)
                break
            
            # Process each feature
            for feature in features:
                props = feature.get("properties", {})
                
                # Determine primary code (ICAO > IATA > WMO > MSC ID)
                icao = props.get("icao_id") or props.get("iata_id")
                iata = props.get("iata_id")
                wmo = props.get("wmo_id")
                msc_id = props.get("msc_id")
                feature_id = feature.get("id")
                
                # Use ICAO if available, else IATA, else WMO (for marine), else MSC ID
                primary_code = icao or iata or wmo or msc_id
                
                if not primary_code:
                    print(f"  WARNING: Station with no identifiable code in {collection}: {props}", file=sys.stderr)
                    continue
                
                # Check if we already have this station
                if primary_code in stations:
                    # Merge sources
                    if "geomet_collections" not in stations[primary_code]:
                        stations[primary_code]["geomet_collections"] = []
                    if collection not in stations[primary_code]["geomet_collections"]:
                        stations[primary_code]["geomet_collections"].append(collection)
                    if "geomet" not in stations[primary_code]["sources_available"]:
                        stations[primary_code]["sources_available"].append("geomet")
                else:
                    # New station
                    station_type = "marine" if collection == "swob-marine-stations" else "airport"
                    stations[primary_code] = {
                        "code": primary_code,
                        "identifiers": {
                            "icao": icao,
                            "iata": iata,
                            "wmo": wmo,
                            "msc_id": msc_id,
                            "feature_id": feature_id,
                            "name": props.get("name") or props.get("name_en") or ""
                        },
                        "location": {
                            "lat": feature.get("geometry", {}).get("coordinates", [None, None])[1],
                            "lon": feature.get("geometry", {}).get("coordinates", [None, None])[0],
                            "elevation_m": None  # SWOB doesn't provide elevation
                        },
                        "sources_available": ["geomet"],
                        "geomet_collections": [collection],
                        "station_type": station_type,
                        "data_provider": props.get("data_provider", "MSC"),
                        "country": "Canada",  # Reasonable assumption for SWOB
                        "province_territory": props.get("province_territory") or ""
                    }
            
            print(f"  Processed {len(features)} features. Total stations: {len(stations)}", file=sys.stderr)
            
            # Stop if we got fewer features than page size (last page)
            if len(features) < PAGE_SIZE:
                print(f"  Last page reached (got {len(features)} features < {PAGE_SIZE}).", file=sys.stderr)
                break
            
            offset += PAGE_SIZE
    
    print(f"SWOB collections complete: {len(stations)} total stations", file=sys.stderr)
    return stations


def fetch_aviationweather_stations() -> Dict[str, dict]:
    """Fetch stations from aviationweather.gov."""
    print("Fetching aviationweather.gov stations...", file=sys.stderr)
    
    # Note: aviationweather.gov doesn't have a direct station list endpoint.
    # For now, we'll use a static list of known US stations north of 40°N from existing config.
    # In production, this would need a different approach.
    
    stations = {}
    
    # Try to read existing metar_stations.json to get US stations
    try:
        config_path = "config/metar_stations.json"
        with open(config_path, "r") as f:
            existing = json.load(f)
        
        for station in existing:
            code = station.get("icao") or station.get("iata")
            if not code:
                continue
            
            # Only include US stations (K* prefix)
            if not code.startswith("K"):
                continue
            
            # Check if already in SWOB (shouldn't be for K* codes, but just in case)
            if code in stations:
                # Mark as dual-source
                if "avwx" not in stations[code]["sources_available"]:
                    stations[code]["sources_available"].append("avwx")
            else:
                # New from aviationweather.gov
                stations[code] = {
                    "code": code,
                    "identifiers": {
                        "icao": code,
                        "iata": station.get("iata") or "",
                        "wmo": station.get("wmo_id") or None,
                        "msc_id": None,
                        "feature_id": None,
                        "name": station.get("name") or ""
                    },
                    "location": {
                        "lat": station.get("lat"),
                        "lon": station.get("lon"),
                        "elevation_m": station.get("elevation_m")
                    },
                    "sources_available": ["avwx"],
                    "geomet_collections": [],
                    "station_type": "airport",
                    "data_provider": "aviationweather.gov",
                    "country": "USA",
                    "province_territory": ""
                }
        
        print(f"  Loaded {len(stations)} US stations from existing config", file=sys.stderr)
        return stations
    
    except FileNotFoundError:
        print(f"  WARNING: Could not read existing config/metar_stations.json", file=sys.stderr)
        return stations


def merge_stations(swob: Dict[str, dict], avwx: Dict[str, dict]) -> Dict[str, dict]:
    """Merge SWOB and aviationweather.gov stations."""
    print("Merging station sources...", file=sys.stderr)
    
    merged = swob.copy()
    
    for code, station in avwx.items():
        if code in merged:
            # Duplicate (unlikely for K* codes but possible for international partner stations)
            if "avwx" not in merged[code]["sources_available"]:
                merged[code]["sources_available"].append("avwx")
        else:
            # New station from aviationweather.gov
            merged[code] = station
    
    print(f"  Total stations after merge: {len(merged)}", file=sys.stderr)
    return merged


def add_metadata(stations: Dict[str, dict]) -> Dict[str, dict]:
    """Add generated_at timestamp and sort by code."""
    result = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "total_stations": len(stations),
        "stations": sorted(stations.values(), key=lambda s: str(s["code"]))
    }
    return result


def save_stations(stations_data: dict, output_path: str = "config/metar_stations.json") -> None:
    """Write stations to JSON file."""
    print(f"Writing to {output_path}...", file=sys.stderr)
    
    try:
        with open(output_path, "w") as f:
            json.dump(stations_data["stations"], f, indent=2)
        
        print(f"SUCCESS: Wrote {stations_data['total_stations']} stations to {output_path}", file=sys.stderr)
        print(f"Generated at: {stations_data['generated_at']}", file=sys.stderr)
        
        # Print summary by source
        source_counts = {}
        for station in stations_data["stations"]:
            for source in station.get("sources_available", []):
                source_counts[source] = source_counts.get(source, 0) + 1
        
        print("\nSummary by source:", file=sys.stderr)
        for source, count in sorted(source_counts.items()):
            print(f"  {source}: {count} stations", file=sys.stderr)
        
    except Exception as e:
        print(f"ERROR writing to {output_path}: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main execution."""
    print("=" * 80, file=sys.stderr)
    print("Generating comprehensive station list from MSC GeoMet and aviationweather.gov", file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    
    # Fetch from both sources
    swob_stations = fetch_swob_stations()
    avwx_stations = fetch_aviationweather_stations()
    
    # Merge
    merged = merge_stations(swob_stations, avwx_stations)
    
    # Add metadata
    final_data = add_metadata(merged)
    
    # Save
    save_stations(final_data)
    
    print("=" * 80, file=sys.stderr)
    print("Station list generation complete!", file=sys.stderr)
    print("=" * 80, file=sys.stderr)


if __name__ == "__main__":
    main()
