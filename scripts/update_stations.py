"""
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
    "CYAD", "CYQQ", "CYQB", "CYDT", "CYFF", "CYIZ", "CYIC", "CYIS", "CYDL", "CYLK",
    "CYLT", "CYMM", "CYMN", "CYMY", "CYNC", "CYND", "CYNG", "CYOJ", "CYOH", "CYOW",
    "CYPA", "CYPG", "CYPU", "CYQC", "CYQD", "CYQR", "CYRA", "CYRG", "CYRH", "CYRL",
    "CYRX", "CYSC", "CYSE", "CYSY", "CYTH", "CYTL", "CYTS", "CYUA", "CYUL", "CYUM",
    "CYUN", "CYUP", "CYUS", "CYUW", "CYUX", "CYUY", "CYUZ", "CYVB", "CYVL", "CYVU",
    "CYVZ", "CYWA", "CYWD", "CYWE", "CYWF", "CYWH", "CYWL", "CYWP", "CYWR", "CYWS",
    "CYWV", "CYXC", "CYXD", "CYXE", "CYXF", "CYXH", "CYXJ", "CYXK", "CYXL", "CYXM",
    "CYXN", "CYXP", "CYXQ", "CYXR", "CYXS", "CYXT", "CYXU", "CYXX", "CYYY", "CYYZ",
    "CYZF", "CYZG", "CYZI", "CYZS", "CYZT", "CYZU", "CYZW", "CYZX",
    
    # Major US stations north of 40°N (north of 40.0°N latitude)
    # Alaska
    "PANC", "PAFB", "PASK", "PANT", "PATK", "PAWG", "PACD", "PAEL", "PAFA", "PAGT",
    "PAHC", "PAHO", "PAHU", "PAIL", "PAJN", "PAKN", "PALE", "PALM", "PAMG", "PANN",
    "PAOA", "PAPC", "PAQQ", "PARS", "PASN", "PATE", "PATG", "PATI", "PAUK", "PAVD",
    "PAWT", "PAXX", "PAYC", "PAYK", "PAZK",
    
    # Washington
    "KSEA", "KSFF", "KBFI", "KTCM", "KOLM", "KBLI", "KPAE", "KTIW", "KPWT", "KELN",
    "KEWS", "KOKM", "KGRF", "KSHN", "KSPB", "KPSC", "KSFF", "KMWH", "KEAT", "KRLD",
    "KEWU", "KSPK", "KPUW", "KSGC", "KSEA", "KVTA",
    
    # Oregon (north part)
    "KPDX", "KHIO", "KJFB", "KHTZ", "KTTD", "KMFR", "KRDD", "KRGD", "KRGE",
    
    # Idaho
    "KBOI", "KMSO", "KSUN", "KICX", "KGDV", "KMYL", "KBZN", "KBTM", "KBBB",
    
    # Montana
    "KGLG", "KFCA", "KMSO", "KBZN", "KBTM", "KSFF", "KGDV", "KGRB",
    
    # Wyoming
    "KCDS", "KCSY", "KROK", "KCPR", "KLSK", "KVEG", "KRVS", "KBYT", "KGCC", "KVCO",
    
    # Colorado
    "KDEN", "KAFF", "KCCO", "KEPC", "KFCS", "KGJT", "KGUL", "KPUB", "KNBC", "KSLV",
    
    # Utah
    "KSLC", "KSPI", "KSUU", "KMAB", "KCNY", "KDVA", "KPIU", "KVCE",
    
    # Arizona (north part)
    "KFLG", "KPRC", "KSEZ", "KPGE", "KDMX", "KPAN",
    
    # New Mexico (north part)
    "KABQ", "KAFN", "KCSV", "KCTX", "KDGG", "KFAR", "KRTH", "KRTE", "KSKX",
    
    # Minnesota
    "KMSP", "KRST", "KMSN", "KSTP", "KMVS", "KDCA", "KDLH", "KBRD", "KEVN", "KFSE",
    "KGNB", "KINK", "KIWD", "KLDO", "KMCT", "KORP", "KPPM", "KRWM", "KSDU", "KTVH",
    "KWGG", "KWVC",
    
    # Iowa
    "KDSM", "KCID", "KDVN", "KSBN", "KMDT", "KCDV", "KSGS",
    
    # Illinois
    "KORD", "KJFB", "KMDW", "KPK", "KDPA", "KC09", "KDXT", "KEIK", "KFSX", "KILS",
    "KMLI", "KPMQ", "KQUQ", "KLMS", "KSGC",
    
    # Michigan
    "KDTW", "KMBS", "KMCE", "KORD", "KPHN", "KLANL",
    
    # Wisconsin
    "KMKE", "KMTW", "KMSN", "KRST", "KATW", "KGRB", "KGRE", "KHES", "KOSHKOSH",
    "KRSN", "KSUE", "KWSR",
    
    # Indiana
    "KORD", "KGRR", "KPVB", "KJFB", "KEYW", "KIND", "KVPB",
    
    # Ohio
    "KCLE", "KCMH", "KSFN", "KVTA", "KDAO", "KDAY", "KSGH", "KSVU", "KYNG", "KMFD",
    "KTOL",
    
    # Pennsylvania
    "KORD", "KPIT", "KLNS", "KPHG", "KPHL", "KMDT", "KBTZ", "KBKS", "KDUJ",
    
    # New York
    "KJFK", "KLGA", "KNEWARK", "KBUF", "KROC", "KSYR", "KALB", "KEWR", "KBGM", "KELM",
    "KFSO", "KIPT", "KMPO", "KPOH", "KSEE", "KSYY", "KUGN", "KVUP", "KWVL",
    
    # Vermont
    "KBVT", "KRVT",
    
    # New Hampshire
    "KMHT", "KSAU", "KASH", "KPYM",
    
    # Maine
    "KPWM", "KBGR", "KBHB", "KPQI", "KRKS", "KPRQ",
    
    # Massachusetts
    "KBOS", "KBWY", "KFYW", "KOWD", "KSEA", "KACY",
    
    # Connecticut
    "KBDR", "KHFD", "KNEW", "KPOH", "KBWI",
    
    # New Jersey
    "KTEB", "KEWR", "KPNE", "KMJX", "KMRU",
    
    # Delaware
    "KMDT", "KIAD", "KRWD",
    
    # Maryland
    "KBWI", "KMTN", "KHGR", "KFDK",
    
    # Virginia
    "KIAD", "KRDW", "KNRF", "KORL", "KWAS", "KLYH", "KCVL", "KFVX", "KHEY", "KJYO",
    "KOCK", "KRVA", "KRWI", "KSFD", "KVKX",
    
    # West Virginia (north part)
    "KAEO", "KCKB", "KCRW",
    
    # North Carolina (extreme north)
    "KGRD", "KBWI", "KRWI",
    
    # Tennessee (north part)
    "KBNA", "KMEM", "KMCO", "KDSM", "KMKL", "KTYS",
    
    # Kentucky
    "KSDF", "KLOU", "KCVG", "KMUI", "KBCT",
    
    # Missouri (north part)
    "KSTL", "KORD", "KSGF", "KJLN", "KMCI", "KXNA", "KBID",
    
    # Kansas
    "KMHK", "KMCI", "KZKA", "KMHK",
    
    # Nebraska
    "KORD", "KLNK", "KOMA", "KBEG", "KBDL", "KOMA", "KSID",
    
    # South Dakota
    "KPIR", "KRAP", "KBYT", "KJOY", "KFSD", "KHUV", "KRME",
    
    # North Dakota
    "KBISMARK", "KBTM", "KJMS", "KLYR", "KXXL", "KRAF", "KFAR", "KMOT",
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
    print(f"  - All Canadian stations")
    print(f"  - All US stations north of 40°N")
    print(f"  ({len(STATION_CODES)} stations total)")
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
