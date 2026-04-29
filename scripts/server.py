"""
Custom HTTP server for fire-weather briefing dashboard.
Serves static files and handles API endpoints including /api/metar for METAR observations.

Usage:
    python scripts/server.py [port]

Default port: 8765
"""

import http.server
import json
import sys
import urllib.parse
import urllib.request
import ssl
from pathlib import Path

# Import the metar handler
sys.path.insert(0, str(Path(__file__).parent))
from metar_handler import handle_metar_request


class DashboardRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP request handler with API routing."""

    def __init__(self, *args, **kwargs):
        # Set base directory to project root
        super().__init__(*args, directory=str(Path(__file__).parent.parent), **kwargs)

    def do_GET(self):
        """Handle GET requests with API routing."""
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query_string = parsed.query

        # Route /api/metar requests to METAR handler
        if path == "/api/metar":
            return self._handle_metar_api(query_string)

        # Route /api/proxy-image requests to image proxy handler
        if path == "/api/proxy-image":
            return self._handle_image_proxy(query_string)

        # All other requests: serve static files
        return super().do_GET()

    def _handle_metar_api(self, query_string):
        """Handle /api/metar API requests."""
        try:
            # Parse query parameters
            params = urllib.parse.parse_qs(query_string)

            # Convert parameter lists to single values
            query_params = {
                "stations": params.get("stations", [""])[0],
                "hours": params.get("hours", ["12"])[0],
                "tz": params.get("tz", ["UTC"])[0],
            }

            # Call metar handler
            response = handle_metar_request(query_params)

            # Send JSON response
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode("utf-8"))

        except Exception as e:
            # Error response with logging
            import traceback
            print(f"METAR API Error: {e}", file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            error_response = {"success": False, "error": str(e)}
            self.wfile.write(json.dumps(error_response).encode("utf-8"))

    def _handle_image_proxy(self, query_string):
        """Proxy satellite images from weather.gc.ca to avoid CORS issues."""
        try:
            # Parse query parameters
            params = urllib.parse.parse_qs(query_string)
            url_path = params.get("url", [""])[0]

            if not url_path:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Missing 'url' parameter"}).encode("utf-8"))
                return

            # Construct full URL - relative paths get prefixed with weather.gc.ca
            if url_path.startswith("/"):
                full_url = f"https://weather.gc.ca{url_path}"
            elif url_path.startswith("http"):
                full_url = url_path
            else:
                full_url = f"https://weather.gc.ca/{url_path}"

            # Fetch the image from weather.gc.ca
            context = ssl.create_default_context()
            request = urllib.request.Request(full_url, headers={"User-Agent": "Mozilla/5.0"})
            
            with urllib.request.urlopen(request, context=context, timeout=30) as response:
                image_data = response.read()
                content_type = response.headers.get("Content-Type", "image/jpeg")

            # Send image response with CORS headers
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "public, max-age=3600")
            self.end_headers()
            self.wfile.write(image_data)

        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"HTTP {e.code}: {e.reason}"}).encode("utf-8"))
        except Exception as e:
            import traceback
            print(f"Image Proxy Error: {e}", file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

    def log_message(self, format, *args):
        """Reduce logging verbosity."""
        # Only log errors and API requests
        if "api" in self.path or "HTTP" not in format:
            return super().log_message(format, *args)


def main():
    """Start the HTTP server."""
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765

    handler = DashboardRequestHandler
    server = http.server.HTTPServer(("127.0.0.1", port), handler)

    print(f"Starting fire-weather briefing server on port {port}...")
    print(f"Dashboard: http://127.0.0.1:{port}/dashboard/index.html")
    print(f"METAR viewer: http://127.0.0.1:{port}/dashboard/metar.html")
    print("Press Ctrl+C to stop")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
