from __future__ import annotations

import re
import ssl
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_PATH = BASE_DIR / "dashboard" / "goes_ir_configured.html"
GOES_URL = "https://weather.gc.ca/satellite/satellite_anim_e.html?sat=goes&area=nam&type=1070"
BASE_HREF = "https://weather.gc.ca/"
LOAD_IMAGES = 37  # last ~6 hours at 10-minute cadence, inclusive of latest frame
SPEED_STEPS = 2


def fetch_html(url: str) -> str:
    context = ssl.create_default_context()
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, context=context, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def configure_html(html: str) -> str:
    if "<base " not in html:
        html = html.replace("<head>", f"<head>\n  <base href=\"{BASE_HREF}\" />", 1)

    html, replacements = re.subn(
        r'(<select[^>]*id="wxo-anim-from-time"[^>]*data-default-load-images=")\d+(")',
        rf'\g<1>{LOAD_IMAGES}\2',
        html,
        count=1,
    )

    if replacements == 0:
        html = re.sub(
            r'(<select[^>]*id="wxo-anim-from-time")',
            rf'\1 data-default-load-images="{LOAD_IMAGES}"',
            html,
            count=1,
        )

    banner = f"""
<div id=\"copilot-goes-note\" style=\"max-width: 1200px; margin: 1rem auto 0; padding: 0.75rem 1rem; border: 1px solid #cfe1f7; border-radius: 12px; background: #edf5ff; color: #183046; font-family: Segoe UI, Arial, sans-serif;\">
  <strong>Configured GOES view:</strong> loading the last ~6 hours of imagery and increasing the animation speed by 2 steps.
  <a href=\"{GOES_URL}\" target=\"_blank\" rel=\"noreferrer\" style=\"margin-left: 0.5rem;\">Open original Environment Canada page</a>
</div>
""".strip()

    if "copilot-goes-note" not in html and "<main" in html:
        html = html.replace("<main", f"{banner}\n<main", 1)

    inject_script = f"""
<script id=\"copilot-goes-config\">
(() => {{
  const desiredLoadImages = {LOAD_IMAGES};
  const speedSteps = {SPEED_STEPS};

  function applyConfiguredView() {{
    const fromSelect = document.getElementById('wxo-anim-from-time');
    const toSelect = document.getElementById('wxo-anim-to-time');
    const fasterButton = document.querySelector('.wxo-anim-faster');
    const slowerButton = document.querySelector('.wxo-anim-slower');
    const playButton = document.getElementById('play');

    if (fromSelect) {{
      fromSelect.dataset.defaultLoadImages = String(desiredLoadImages);
    }}

    if (fromSelect && toSelect && toSelect.options.length) {{
      const latestValue = Number.parseInt(
        toSelect.value || toSelect.options[toSelect.options.length - 1].value || '0',
        10
      );
      const earliestValue = Math.max(0, latestValue - (desiredLoadImages - 1));

      toSelect.value = String(latestValue);
      fromSelect.value = String(earliestValue);
      fromSelect.dispatchEvent(new Event('change', {{ bubbles: true }}));
      toSelect.dispatchEvent(new Event('change', {{ bubbles: true }}));
    }}

    if (speedSteps > 0 && fasterButton) {{
      for (let i = 0; i < speedSteps; i += 1) {{
        fasterButton.click();
      }}
    }}

    if (speedSteps < 0 && slowerButton) {{
      for (let i = 0; i < Math.abs(speedSteps); i += 1) {{
        slowerButton.click();
      }}
    }}

    playButton?.click();
  }}

  window.addEventListener('load', () => {{
    window.setTimeout(applyConfiguredView, 300);
    window.setTimeout(applyConfiguredView, 1400);
  }});
}})();
</script>
""".strip()

    if "copilot-goes-config" not in html:
        html = html.replace("</body>", f"\n{inject_script}\n</body>", 1)

    # Inject GIF download button and scripts
    gif_download_button = """
<div id=\"copilot-gif-download-row\" class=\"row wxo-nojs-hide hidden\" style=\"margin-top: 0.5rem;\">
  <div class=\"col-lg-4 col-md-4 col-sm-6 col-xs-12 mrgn-bttm-md mrgn-lft-md\">
    <button id=\"gif-download-btn\" class=\"btn btn-success btn-sm\" title=\"Download as animated GIF for PowerPoint\">
      <span class=\"glyphicon glyphicon-download\"></span>
      <span class=\"wb-inv\">Download as GIF</span>
      <span>Download as GIF</span>
    </button>
    <span id=\"gif-download-status\" class=\"mrgn-lft-md\" style=\"font-size: 0.9em; display: inline-block;\"></span>
  </div>
</div>
""".strip()

    gif_scripts = """
<!-- GIF Download Feature -->
<script>
  // Load gif.js from local server (avoids tracking prevention blocking CDN)
  const gifScript = document.createElement('script');
  gifScript.src = new URL('/lib/gif.js', window.location.href).href;
  gifScript.onload = () => {
    // gif.js loaded, now load gif-download.js from local server
    const appScript = document.createElement('script');
    appScript.src = new URL('/dashboard/gif-download.js', window.location.href).href;
    document.head.appendChild(appScript);
  };
  document.head.appendChild(gifScript);
</script>
""".strip()

    if "copilot-gif-download" not in html:
        # Insert button after speed controls (look for Reset Speed button)
        if "Reset Speed" in html and "wxo-anim-speed-reset" in html:
            html = html.replace("Reset Speed</button>", f"Reset Speed</button>\n{gif_download_button}", 1)
        
        # Inject scripts before closing body tag
        html = html.replace("</body>", f"\n{gif_scripts}\n</body>", 1)

    return html


def fallback_html(error: Exception) -> str:
    return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>Configured GOES IR view</title>
  <style>
    body {{ font-family: Segoe UI, Arial, sans-serif; margin: 2rem; color: #183046; background: #f3f7fb; }}
    .card {{ max-width: 860px; margin: 0 auto; background: white; border: 1px solid #d7e3ef; border-radius: 14px; padding: 1.25rem; }}
    a {{ color: #005ea5; }}
    code {{ background: #eef4fb; padding: 0.15rem 0.35rem; border-radius: 6px; }}
  </style>
</head>
<body>
  <div class=\"card\">
    <h1>Configured GOES IR view</h1>
    <p>The customized local copy could not be refreshed this time.</p>
    <p><strong>Reason:</strong> <code>{error}</code></p>
    <p><a href=\"{GOES_URL}\" target=\"_blank\" rel=\"noreferrer\">Open the original Environment Canada GOES page</a></p>
  </div>
</body>
</html>
"""


def main() -> None:
    try:
        html = fetch_html(GOES_URL)
        output = configure_html(html)
    except Exception as exc:  # pragma: no cover - operational fallback
        output = fallback_html(exc)

    OUTPUT_PATH.write_text(output, encoding="utf-8")
    print(f"Wrote configured GOES page to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
