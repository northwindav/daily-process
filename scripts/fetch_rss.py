from __future__ import annotations

import json
import ssl
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

KEYWORDS = [
    "wildfire",
    "wild fire",
    "forest fire",
    "brush fire",
    "grass fire",
    "smoke",
    "evacuation",
    "evacuate",
    "fire ban",
    "out of control",
]
MAX_ITEMS = 15
BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = BASE_DIR / "config" / "sources.json"
OUTPUT_PATH = BASE_DIR / "data" / "news.json"
ATOM_NS = "{http://www.w3.org/2005/Atom}"


def load_feed_sources() -> list[dict]:
    data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return [source for source in data.get("sources", []) if source.get("feedUrl")]


def fetch_feed(url: str) -> bytes:
    context = ssl.create_default_context()
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, context=context, timeout=20) as response:
        return response.read()


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None

    raw = value.strip()
    if not raw:
        return None

    try:
        if raw.endswith("Z"):
            raw = raw[:-1] + "+00:00"
        parsed = datetime.fromisoformat(raw)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed
    except ValueError:
        try:
            parsed = parsedate_to_datetime(raw)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed
        except (TypeError, ValueError):
            return None


def parse_items(feed_bytes: bytes) -> list[dict]:
    root = ET.fromstring(feed_bytes)
    items: list[dict] = []

    for item in root.findall(".//item"):
        published = parse_datetime(item.findtext("pubDate"))
        items.append(
            {
                "title": (item.findtext("title") or "").strip(),
                "link": (item.findtext("link") or "").strip(),
                "published": published.isoformat() if published else None,
                "description": (item.findtext("description") or "").strip(),
            }
        )

    for entry in root.findall(f".//{ATOM_NS}entry"):
        link = ""
        for candidate in entry.findall(f"{ATOM_NS}link"):
            href = candidate.attrib.get("href", "").strip()
            if href:
                link = href
                break

        published = parse_datetime(entry.findtext(f"{ATOM_NS}updated") or entry.findtext(f"{ATOM_NS}published"))
        items.append(
            {
                "title": (entry.findtext(f"{ATOM_NS}title") or "").strip(),
                "link": link,
                "published": published.isoformat() if published else None,
                "description": (
                    entry.findtext(f"{ATOM_NS}summary")
                    or entry.findtext(f"{ATOM_NS}content")
                    or ""
                ).strip(),
            }
        )

    return items


def is_recent(item: dict, now: datetime) -> bool:
    published = item.get("published")
    if not published:
        return False

    timestamp = datetime.fromisoformat(published)
    return timestamp >= now - timedelta(hours=24)


def matches_keywords(item: dict) -> bool:
    haystack = f"{item.get('title', '')} {item.get('description', '')}".lower()
    return any(keyword in haystack for keyword in KEYWORDS)


def main() -> None:
    now = datetime.now(timezone.utc)
    feed_sources = load_feed_sources()
    results: list[dict] = []
    errors: list[dict] = []
    seen: set[str] = set()

    for source in feed_sources:
        try:
            raw = fetch_feed(source["feedUrl"])
            items = parse_items(raw)
        except Exception as exc:  # pragma: no cover - operational fallback
            errors.append({"source": source["label"], "message": str(exc)})
            continue

        for item in items:
            if not is_recent(item, now) or not matches_keywords(item):
                continue

            unique_key = item.get("link") or item.get("title")
            if not unique_key or unique_key in seen:
                continue

            seen.add(unique_key)
            results.append(
                {
                    **item,
                    "source": source["label"],
                    "sourceUrl": source.get("url", ""),
                }
            )

    results.sort(key=lambda item: item.get("published") or "", reverse=True)
    results = results[:MAX_ITEMS]

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(
            {
                "generatedAt": now.isoformat(),
                "keywords": KEYWORDS,
                "feedCount": len(feed_sources),
                "itemCount": len(results),
                "errors": errors,
                "items": results,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        f"Checked {len(feed_sources)} feed(s), kept {len(results)} headline(s), "
        f"and recorded {len(errors)} feed error(s) in {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()
