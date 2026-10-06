import csv
import hashlib
import re
from pathlib import Path
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen

def clean_text(text: str) -> str:
    """Normalize whitespace and remove simple HTML tags."""
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", text).strip()


def load_csv_records(path: str | Path, source_name: str) -> list[dict]:
    """
    Load CSV rows with a `text` column.

    The file may optionally contain a `source` column. If present, that
    value is retained; otherwise `source_name` is used.
    """
    records = []
    with Path(path).open(newline="", encoding="utf-8-sig") as file:
        for row in csv.DictReader(file):
            text = clean_text(row.get("text", ""))
            if not text:
                continue

            records.append({
                "source": row.get("source") or source_name,
                "text": text,
                "record_id": row.get("id") or hashlib.sha256(
                    text.lower().encode("utf-8")
                ).hexdigest()[:16],
            })

    return records


def deduplicate_records(records: list[dict]) -> list[dict]:
    """Keep the first record for each normalized text string."""
    unique = []
    seen = set()

    for record in records:
        key = re.sub(r"\s+", " ", record["text"].lower()).strip()
        if key not in seen:
            seen.add(key)
            unique.append(record)

    return unique


def load_all_sources(source_files: dict[str, str | Path]) -> list[dict]:
    """Load and deduplicate multiple local CSV sources."""
    records = []
    for source_name, path in source_files.items():
        records.extend(load_csv_records(path, source_name))
    return deduplicate_records(records)

def fetch_gdelt_news(query: str = "TSMC OR semiconductor OR banking", limit: int = 10) -> list[dict]:
    """Fetch recent article titles from GDELT DOC API (no API key required)."""
    params = urlencode({
        "query": query,
        "mode": "artlist",
        "format": "json",
        "sort": "datedesc",
        "maxrecords": min(limit, 50),
    })
    url = f"https://api.gdeltproject.org/api/v2/doc/doc?{params}"

    request = Request(
        url,
        headers={"User-Agent": "RiskPulseAI/0.1 (hackathon demo)"},
    )

    try:
        with urlopen(request, timeout=15) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception as error:
        raise RuntimeError(f"GDELT news fetch failed: {error}") from error

    records = []
    for article in payload.get("articles", []):
        title = clean_text(article.get("title", ""))
        if not title:
            continue

        records.append({
            "source": "gdelt",
            "text": title,
            "url": article.get("url", ""),
            "published_at": article.get("seendate", ""),
            "record_id": article.get("url", title),
        })

    return records