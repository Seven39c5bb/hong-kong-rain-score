# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Fetch the two published source files once; preserve their original bytes."""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
SOURCES = {
    "dailyExtract_2025.xml": "https://www.hko.gov.hk/cis/dailyExtract/dailyExtract_2025.xml",
    "dailyExtract-source.html": "https://www.hko.gov.hk/en/cis/dailyExtract.htm?y=2025&m=1",
}


def fetch_once(filename, url):
    """Return the cached bytes, or download and validate one response before saving."""
    path = DATA / filename
    if path.exists():
        print(f"Using committed source: data/{filename}")
        return path.read_bytes()
    request = Request(url, headers={"User-Agent": "SD5913 Hong Kong Rain Score student project"})
    with urlopen(request, timeout=45) as response:
        raw = response.read()
    if filename.endswith(".xml"):
        # The publisher uses .xml, but the response actually contains JSON.
        content = json.loads(raw)
        if len(content["stn"]["data"]) != 12:
            raise ValueError("Expected twelve monthly blocks; source was not saved.")
    elif b"Total Rainfall (mm)" not in raw or b"Trace means rainfall" not in raw:
        raise ValueError("Source page no longer documents the expected rainfall fields.")
    DATA.mkdir(exist_ok=True)
    path.write_bytes(raw)
    print(f"Saved raw response: data/{filename} ({len(raw):,} bytes)")
    return raw


def main():
    sources = []
    for filename, url in SOURCES.items():
        raw = fetch_once(filename, url)
        sources.append({"file": filename, "url": url, "bytes": len(raw),
                        "sha256": hashlib.sha256(raw).hexdigest()})
    manifest = DATA / "provenance.json"
    if not manifest.exists():
        metadata = {
            "manifest_created_utc": datetime.now(timezone.utc).isoformat(),
            "note": "This manifest is project metadata, not a publisher response. Source files are unmodified.",
            "sources": sources,
        }
        manifest.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    else:
        recorded = json.loads(manifest.read_text(encoding="utf-8"))["sources"]
        if sources != recorded:
            raise ValueError("Cached source bytes differ from the recorded provenance hashes.")


if __name__ == "__main__":
    main()
