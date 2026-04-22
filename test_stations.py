import urllib.request
import json

# All 49 successful Canadian stations + 34 US north of 40N
all_stations = [
    # 49 Canadian stations confirmed on aviationweather.gov
    "CYAT", "CYBK", "CYCA", "CYCD", "CYCK", "CYEG", "CYFB", "CYFS", "CYGK", "CYHZ",
    "CYMM", "CYOJ", "CYOW", "CYPA", "CYPH", "CYPO", "CYPR", "CYQB", "CYQU", "CYQX",
    "CYRJ", "CYSB", "CYTH", "CYTL", "CYUL", "CYUX", "CYVL", "CYVR", "CYWA", "CYWG",
    "CYWH", "CYWL", "CYXC", "CYXE", "CYXH", "CYXJ", "CYXL", "CYXR", "CYXS", "CYXT",
    "CYXU", "CYXX", "CYXY", "CYYC", "CYYT", "CYYY", "CYYZ", "CYZF", "CYZS",
    # 34 US stations north of 40N
    "KSEA", "KORD", "KJFK", "KBOS", "KLGA", "KPHL", "KDEN", "KMSP", "KBWI", "KDTW",
    "KCLE", "KMCI", "KSTL", "KSLC", "KPDX", "KBOI", "KMSO", "KBZN", "KABQ", "KBUF",
    "KRDU", "KATL", "KIAD", "KDCA", "KMCO", "KDFW", "KIAH", "KSFO", "KLAX", "KFSD",
    "KRSN", "KFAR", "KRMT", "KSPK",
]

API_METAR_URL = "https://aviationweather.gov/api/data/metar"
USER_AGENT = "fire-weather-briefing/1.0 (+https://aviationweather.gov/data/api/)"

stations_data = {}
batch_size = 10

for i in range(0, len(all_stations), batch_size):
    batch = all_stations[i:i+batch_size]
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
                            "country": "Canada" if icao_id.startswith("C") else "United States",
                            "lat": obs.get("lat"),
                            "lon": obs.get("lon"),
                            "elevation_m": obs.get("elev"),
                        }
    except Exception as e:
        print(f"  Batch error: {e}")

# Filter for those with coordinates and sort
filtered = [s for s in stations_data.values() if s.get("lat") is not None and s.get("lon") is not None]
filtered.sort(key=lambda s: (s["country"], s["region"], s["icao"]))

print(f"Total stations retrieved: {len(filtered)}")
ca = [s for s in filtered if s["country"] == "Canada"]
us = [s for s in filtered if s["country"] == "United States"]
print(f"Canadian: {len(ca)}, US: {len(us)}")

with open("config/metar_stations.json", "w") as f:
    json.dump(filtered, f, indent=2)
print(f"✓ Saved {len(filtered)} stations to config/metar_stations.json")

