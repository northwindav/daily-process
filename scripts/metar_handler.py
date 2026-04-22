"""
METAR API handler for the Fire-Weather Dashboard.
Queries aviationweather.gov for recent observations and formats as JSON.
"""

import json
import math
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from typing import Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

# Configuration
API_URL = "https://aviationweather.gov/api/data/metar"
API_TIMEOUT_SECONDS = 5
MAX_HOURS = 48
USER_AGENT = "fire-weather-briefing/1.0 (+https://aviationweather.gov/data/api/)"

# Timezone abbreviation mappings
TIMEZONE_MAP = {
    "utc": "UTC",
    "gmt": "UTC",
    "pdt": "America/Los_Angeles",
    "pst": "America/Los_Angeles",
    "mdt": "America/Denver",
    "mst": "America/Denver",
    "cdt": "America/Chicago",
    "cst": "America/Chicago",
    "edt": "America/New_York",
    "est": "America/New_York",
    "ndt": "America/St_Johns",
    "nst": "America/St_Johns",
}


def normalize_timezone(tz_str: str) -> str:
    """
    Convert timezone abbreviation or IANA name to IANA name.
    
    Args:
        tz_str: Timezone abbreviation (pdt, est, utc) or IANA name (America/Vancouver)
        
    Returns:
        IANA timezone name, or raises ZoneInfoNotFoundError if invalid
    """
    tz_lower = tz_str.lower()
    
    # Try abbreviation map first
    if tz_lower in TIMEZONE_MAP:
        return TIMEZONE_MAP[tz_lower]
    
    # Try as IANA name (validate by creating ZoneInfo)
    try:
        ZoneInfo(tz_str)
        return tz_str
    except ZoneInfoNotFoundError:
        raise ZoneInfoNotFoundError(f"Unknown timezone: {tz_str}")


def query_metar(stations: list[str], hours: int, tz: str) -> dict:
    """
    Query aviationweather.gov for METAR observations.
    
    Args:
        stations: List of ICAO station codes (e.g., ["CYYZ", "CYUL"])
        hours: Number of hours to retrieve (1-48)
        tz: Timezone for display (abbreviation or IANA name)
        
    Returns:
        Dictionary with structure:
        {
            "success": bool,
            "data": [{
                "icao": str,
                "observations": [{
                    "time": str,
                    "temp_c": float,
                    "dewpoint_c": float,
                    "rh_percent": float,
                    "wind_dir": str,
                    "wind_speed_kt": float,
                    "visibility_m": float,
                    "pressure_hpa": float,
                    "weather": str,
                    "clouds": str,
                    "remarks": str
                }]
            }],
            "error": str (if success=false)
        }
    """
    import sys
    
    # Validate inputs
    if not stations or len(stations) == 0:
        return {"success": False, "error": "No stations provided"}
    
    if hours < 1 or hours > MAX_HOURS:
        return {"success": False, "error": f"Hours must be between 1 and {MAX_HOURS}"}
    
    # Normalize and validate timezone
    try:
        tz_name = normalize_timezone(tz)
        tz_info = ZoneInfo(tz_name)
    except ZoneInfoNotFoundError as e:
        return {"success": False, "error": str(e)}
    
    # Build API query
    station_param = ",".join([s.upper() for s in stations])
    params = {
        "ids": station_param,
        "format": "json",
        "hours": hours,
    }
    
    query_string = urllib.parse.urlencode(params)
    url = f"{API_URL}?{query_string}"
    
    # Create request with custom User-Agent
    req = urllib.request.Request(url)
    req.add_header("User-Agent", USER_AGENT)
    
    # Query API
    try:
        with urllib.request.urlopen(req, timeout=API_TIMEOUT_SECONDS) as response:
            raw_data = response.read()
            
            # Check if response is empty
            if not raw_data:
                station_str = ",".join(stations)
                print(f"DEBUG: Empty response from API for stations {station_str}", file=sys.stderr)
                return {"success": False, "error": f"No data available for {station_str}"}
            
            try:
                api_response = json.loads(raw_data)
            except json.JSONDecodeError as json_err:
                # Try to decode raw_data as UTF-8 to see what we got
                try:
                    response_text = raw_data.decode('utf-8', errors='ignore')[:200]
                    print(f"DEBUG: Non-JSON response: {response_text}", file=sys.stderr)
                except:
                    pass
                station_str = ",".join(stations)
                return {"success": False, "error": f"No data available for {station_str}"}
    except urllib.error.URLError as e:
        return {"success": False, "error": f"API connection failed: {e.reason}"}
    except Exception as e:
        print(f"DEBUG: Unexpected API error: {str(e)}", file=sys.stderr)
        station_str = ",".join(stations)
        return {"success": False, "error": f"No data available for {station_str}"}
    
    # Parse API response and format observations
    # Handle both dict response with "results" key and direct array response
    results = []
    
    if isinstance(api_response, list):
        metar_data = api_response
    elif isinstance(api_response, dict):
        metar_data = api_response.get("results", [])
    else:
        return {"success": False, "error": "Unexpected API response format"}
    
    # Check for empty response
    if not metar_data or len(metar_data) == 0:
        station_str = ",".join(stations)
        print(f"DEBUG: No data returned from API for stations {station_str}", file=sys.stderr)
        return {"success": False, "error": f"No data available for {station_str}"}
    
    # Group observations by station
    stations_dict = {}
    
    for obs in metar_data:
        # Ensure obs is a dict
        if not isinstance(obs, dict):
            continue
        
        icao_id = obs.get("icaoId")
        if not icao_id:
            continue
        
        # Initialize station entry if needed
        if icao_id not in stations_dict:
            stations_dict[icao_id] = {
                "name": obs.get("name", ""),
                "lat": obs.get("lat"),
                "lon": obs.get("lon"),
                "elev": obs.get("elev"),
                "observations": []
            }
        
        try:
            # Parse observation timestamp (UNIX epoch or ISO 8601)
            obs_time_raw = obs.get("obsTime")
            
            if isinstance(obs_time_raw, (int, float)):
                # UNIX timestamp
                obs_time_utc = datetime.fromtimestamp(obs_time_raw, tz=timezone.utc)
            else:
                # Try ISO format
                obs_time_utc = datetime.fromisoformat(str(obs_time_raw).replace("Z", "+00:00"))
            
            # Convert to target timezone
            obs_time_local = obs_time_utc.astimezone(tz_info)
            time_str = obs_time_local.strftime("%Y-%m-%d %H:%M %Z")
            
            # Extract fields (note: field names differ from expected)
            temp_c = obs.get("temp")
            dewpoint_c = obs.get("dewp")
            
            # Calculate relative humidity if possible
            rh = None
            if temp_c is not None and dewpoint_c is not None:
                try:
                    # Convert to float if needed
                    temp_float = float(temp_c)
                    dewp_float = float(dewpoint_c)
                    # Magnus approximation for RH
                    # RH = 100 * exp(f(Td) - f(T)) where f(T) = (a*T)/(b+T)
                    a, b = 17.27, 237.7
                    f_td = (a * dewp_float) / (b + dewp_float)
                    f_t = (a * temp_float) / (b + temp_float)
                    rh = 100 * math.exp(f_td - f_t)
                    rh = round(rh, 1)
                    # Clamp to 0-100%
                    rh = max(0, min(100, rh))
                except (ValueError, TypeError) as e:
                    print(f"DEBUG: RH calc error for {icao_id}: {e}", file=sys.stderr)
                    rh = None
            
            # Wind (convert from knots to km/h)
            wind_dir = obs.get("wdir")
            wind_speed_kt = obs.get("wspd")
            wind_gust_kt = obs.get("wgst")
            wind_str = ""
            if wind_speed_kt is not None:
                try:
                    # Convert knots to km/h (handle both float and string)
                    wind_speed_kmh = int(float(wind_speed_kt) * 1.852)
                    if wind_gust_kt is not None:
                        wind_gust_kmh = int(float(wind_gust_kt) * 1.852)
                        wind_speed_str = f"{wind_speed_kmh}G{wind_gust_kmh}"
                    else:
                        wind_speed_str = str(wind_speed_kmh)
                    
                    # Handle variable (VRB) wind direction
                    if wind_dir is not None and wind_dir != "VRB":
                        try:
                            wind_str = f"{wind_speed_str} @ {int(float(wind_dir)):03d}°"
                        except (ValueError, TypeError):
                            wind_str = wind_speed_str
                    else:
                        wind_str = wind_speed_str
                except (ValueError, TypeError):
                    wind_str = ""
            
            # Visibility (in statute miles, keep as-is)
            visibility_sm = obs.get("visib")
            visibility_str = ""
            if visibility_sm is not None:
                # Handle both numeric and string values (e.g., "10+")
                try:
                    if isinstance(visibility_sm, str):
                        visibility_str = visibility_sm
                    else:
                        visibility_str = str(int(visibility_sm))
                except (ValueError, TypeError):
                    visibility_str = str(visibility_sm)
            
            # Pressure (SLP in hPa)
            pressure_hpa = obs.get("slp")
            pressure_str = ""
            if pressure_hpa is not None:
                try:
                    pressure_str = f"{float(pressure_hpa):.1f}"
                except (ValueError, TypeError):
                    pressure_str = str(pressure_hpa)
            
            # Weather
            weather_str = obs.get("wxString", "") or ""
            
            # Clouds
            clouds_list = obs.get("clouds", [])
            clouds_str = ""
            if clouds_list:
                cloud_layers = []
                for layer in clouds_list:
                    if isinstance(layer, dict):
                        cover = layer.get("cover", "")
                        alt = layer.get("base", "")
                        if cover:
                            cloud_layers.append(f"{cover}" + (f"@{alt}ft" if alt else ""))
                clouds_str = ", ".join(cloud_layers)
            
            # Remarks (extract text after 'RMK' from rawOb)
            raw_ob = obs.get("rawOb", "")
            remarks = ""
            if "RMK" in raw_ob:
                remarks = raw_ob.split("RMK", 1)[1].strip()
            
            stations_dict[icao_id]["observations"].append({
                "time": time_str,
                "temp_c": temp_c,
                "dewpoint_c": dewpoint_c,
                "rh_percent": rh,
                "wind": wind_str,
                "visibility": visibility_str,
                "pressure": pressure_str,
                "weather": weather_str,
                "clouds": clouds_str,
                "remarks": remarks
            })
        except Exception as e:
            # Skip observations that fail parsing
            print(f"DEBUG: Error parsing observation for {icao_id}: {e}", file=sys.stderr)
            continue
    
    # Build results from grouped observations
    for icao_id, station_info in stations_dict.items():
        observations = station_info["observations"]
        if observations:
            results.append({
                "icao": icao_id,
                "name": station_info.get("name", ""),
                "lat": station_info.get("lat"),
                "lon": station_info.get("lon"),
                "elev": station_info.get("elev"),
                "observations": observations
            })
    
    return {
        "success": True,
        "data": results,
        "error": None
    }


def handle_metar_request(query_params: dict) -> dict:
    """
    HTTP request handler for /api/metar endpoint.
    
    Query parameters:
        - stations: Comma-separated ICAO codes (required)
        - hours: Number of hours (1-48, default 12)
        - tz: Timezone abbreviation or IANA name (default UTC)
        
    Returns:
        JSON-serializable dictionary
    """
    
    # Extract and validate query parameters
    if not isinstance(query_params, dict):
        return {"success": False, "error": "Invalid request format"}
    
    stations_str = query_params.get("stations", "").strip()
    if not stations_str:
        return {"success": False, "error": "Missing parameter: stations"}
    
    stations = [s.strip().upper() for s in stations_str.split(",")]
    
    try:
        hours_input = query_params.get("hours", "12")
        hours = int(hours_input) if isinstance(hours_input, str) else hours_input
    except (ValueError, TypeError):
        return {"success": False, "error": "Invalid hours parameter (must be integer)"}
    
    tz = query_params.get("tz", "UTC")
    tz = tz.strip() if isinstance(tz, str) else "UTC"
    
    # Call main query function
    return query_metar(stations, hours, tz)
