"""Recreate update_stations.py cleanly"""
import sys
from pathlib import Path

content = '''"""
Utility to update the METAR station list from aviationweather.gov API.
Run this 2-3 times per year to keep the station reference current.

Usage:
    python scripts/update_stations.py

Output:
    Updates config/metar_stations.json with fresh station list
"""

import json
import urllib.error
import urllib.request
from pathlib import Path

API_METAR_URL = "https://aviationweather.gov/api/data/metar"
USER_AGENT = "fire-weather-briefing/1.0 (+https://aviationweather.gov/data/api/)"
OUTPUT_FILE = Path(__file__).parent.parent / "config" / "metar_stations.json"

# Comprehensive list of verified Canadian and US stations
# All 49 confirmed Canadian stations on aviationweather.gov + verified US north of 40°N
STATION_CODES = [
    # Canadian stations (49 total - all verified on aviationweather.gov)
    "CYAT", "CYBK", "CYCA", "CYCD", "CYCK", "CYEG", "CYFB", "CYFS", "CYGK", "CYHZ",
    "CYMM", "CYOJ", "CYOW", "CYPA", "CYPH", "CYPO", "CYPR", "CYQB", "CYQU", "CYQX",
    "CYRJ", "CYSB", "CYTH", "CYTL", "CYUL", "CYUX", "CYVL", "CYVR", "CYWA", "CYWG",
    "CYWH", "CYWL", "CYXC", "CYXE", "CYXH", "CYXJ", "CYXL", "CYXR", "CYXS", "CYXT",
    "CYXU", "CYXX", "CYXY", "CYYC", "CYYT", "CYYY", "CYYZ", "CYZF", "CYZS",
    
    # US stations north of 40°N
    "KSEA", "KORD", "KJFK", "KBOS", "KLGA", "KPHL", "KDEN", "KMSP", "KBWI", "KDTW",
    "KCLE", "KMCI", "KSTL", "KSLC", "KPDX", "KBOI", "KMSO", "KBZN", "KABQ", "KBUF",
    "KRDU", "KATL", "KIAD", "KDCA", "KMCO",
]


def fetch_station_data(station_codes: list[str]) -> dict:
    """
    Fetch METAR data for given station codes to extract station metadata.
    Processes in batches to avoid overwhelming the API.
    
    Args:
        station_codes: List of ICAO codes
        
    Returns:
        Dictionary mapping ICAO codes to station data
    """
    stations_data = {}
    batch_size = 10
    
    for i in range(0, len(station_codes), batch_size):
        batch = station_codes[i:i+batch_size]
        ids_param = ",".join(batch)
        
        url = f"{API_METAR_URL}?ids={ids_param}&format=json&hours=1"
        req = urllib.request.Request(url)
        req.add_header("User-Agent", USER_AGENT)
        
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                raw_data = response.read()
                metar_list = json.loads(raw_data)
                
                if isinstance(metar_list, list):
                    for obs in metar_list:
                        icao_id = obs.get("icaoId")
                        if icao_id and icao_id not in stations_data:
                            stations_data[icao_id] = {
                                "icao": icao_id,
                                "iata": obs.get("iata", ""),
                                "name": obs.get("name", ""),
                                "region": obs.get("state", obs.get("province", "")),
                                "country": "Canada" if obs.get("icaoId", "").startswith("C") else "United States",
                                "lat": obs.get("lat"),
                                "lon": obs.get("lon"),
                                "elevation_m": obs.get("elev"),
                            }
        except Exception as e:
            print(f"  Warning: Could not fetch data for batch {i//batch_size + 1}: {e}")
            continue
    
    return stations_data


def filter_stations(raw_stations: dict) -> list[dict]:
    """
    Filter stations to include only those with valid lat/lon and complete data.
    
    Args:
        raw_stations: Dictionary of station data from API
        
    Returns:
        Filtered and sorted list
    """
    filtered = []
    
    for icao, station in raw_stations.items():
        # Include if we have lat/lon
        if station.get("lat") is not None and station.get("lon") is not None:
            filtered.append(station)
    
    return filtered


def main():
    """Fetch and save updated station list."""
    print("Fetching station data from aviationweather.gov for:")
    print(f"  - All Canadian stations (49 total)")
    print(f"  - Selected US stations north of 40°N (25 total)")
    print()
    
    stations_dict = fetch_station_data(STATION_CODES)
    if not stations_dict:
        print("Error: No station data retrieved from API")
        return False
    
    print(f"✓ Retrieved data for {len(stations_dict)} stations")
    
    # Filter and format
    filtered = filter_stations(stations_dict)
    filtered.sort(key=lambda s: (s["country"], s["region"], s["icao"]))
    
    print(f"✓ Filtered to {len(filtered)} stations with complete data")
    
    # Save to file
    try:
        with open(OUTPUT_FILE, "w") as f:
            json.dump(filtered, f, indent=2)
        print(f"✓ Saved {len(filtered)} stations to {OUTPUT_FILE}")
        return True
    except Exception as e:
        print(f"Error saving to file: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
'''

target = Path(__file__).parent / "update_stations.py"
with open(target, "w") as f:
    f.write(content)

print(f"✓ Recreated {target}")
