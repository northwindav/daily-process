"""
Convert metar_stations.json to human-readable CSV for discovery.
"""

import json
import csv

# Read the JSON file
with open("config/metar_stations.json", "r") as f:
    stations = json.load(f)

# Open CSV for writing
with open("config/metar_stations.csv", "w", newline="") as csvfile:
    fieldnames = [
        "code",
        "name",
        "icao",
        "iata",
        "wmo",
        "msc_id",
        "country",
        "province_territory",
        "lat",
        "lon",
        "station_type",
        "sources_available",
        "data_provider"
    ]
    
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    
    for station in stations:
        writer.writerow({
            "code": station.get("code", ""),
            "name": station.get("identifiers", {}).get("name", ""),
            "icao": station.get("identifiers", {}).get("icao", ""),
            "iata": station.get("identifiers", {}).get("iata", ""),
            "wmo": station.get("identifiers", {}).get("wmo", ""),
            "msc_id": station.get("identifiers", {}).get("msc_id", ""),
            "country": station.get("country", ""),
            "province_territory": station.get("province_territory", ""),
            "lat": station.get("location", {}).get("lat", ""),
            "lon": station.get("location", {}).get("lon", ""),
            "station_type": station.get("station_type", ""),
            "sources_available": ",".join(station.get("sources_available", [])),
            "data_provider": station.get("data_provider", "")
        })

print(f"CSV generated: config/metar_stations.csv")
print(f"Total stations: {len(stations)}")
