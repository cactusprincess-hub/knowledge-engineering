#!/usr/bin/env python3
"""Fetch software-related entities from Wikidata via SPARQL."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import ssl
from urllib.parse import urlencode
from urllib.request import HTTPSHandler, ProxyHandler, Request, build_opener
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

try:
    import requests
except ImportError:  # pragma: no cover - standard-library fallback for minimal environments
    requests = None

from software_ai_kg.io_utils import save_json

SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"

SOFTWARE_QUERY = """
SELECT ?item ?itemLabel ?instance ?instanceLabel ?description WHERE {
  {
    SELECT DISTINCT ?item ?instance WHERE {
      ?item wdt:P31 ?instance.
      ?instance wdt:P279* wd:{class_qid}.
    }
    LIMIT {limit}
    OFFSET {offset}
  }
  OPTIONAL { ?item schema:description ?description FILTER(LANG(?description) = "en") }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en,zh". }
}
""".strip()


def discover_proxies() -> dict[str, str]:
    proxies = {}
    http_proxy = os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy")
    https_proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")

    if http_proxy:
        proxies["http"] = http_proxy
    if https_proxy:
        proxies["https"] = https_proxy
    if proxies:
        return proxies

    try:
        result = subprocess.run(
            ["scutil", "--proxy"],
            capture_output=True,
            check=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return proxies

    lines = result.stdout.splitlines()
    proxy_host = None
    proxy_port = None
    https_enabled = False
    http_enabled = False

    for line in lines:
        normalized = line.strip()
        if normalized.startswith("HTTPEnable :"):
            http_enabled = normalized.endswith("1")
        elif normalized.startswith("HTTPProxy :"):
            proxy_host = normalized.split(":", 1)[1].strip()
        elif normalized.startswith("HTTPPort :"):
            proxy_port = normalized.split(":", 1)[1].strip()
        elif normalized.startswith("HTTPSEnable :"):
            https_enabled = normalized.endswith("1")

    if proxy_host and proxy_port:
        proxy_url = f"http://{proxy_host}:{proxy_port}"
        if http_enabled:
            proxies["http"] = proxy_url
        if https_enabled:
            proxies["https"] = proxy_url
    return proxies


def fetch_entities(
    limit: int,
    offset: int = 0,
    class_qid: str = "Q7397",
    retries: int = 3,
    sleep_seconds: int = 3,
    insecure: bool = False,
) -> dict:
    query = (
        SOFTWARE_QUERY
        .replace("{class_qid}", class_qid)
        .replace("{limit}", str(limit))
        .replace("{offset}", str(offset))
    )
    headers = {
        "Accept": "application/sparql-results+json",
        "User-Agent": "software-ai-kg-course-project/0.1"
    }
    proxies = discover_proxies()

    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            if requests is not None:
                response = requests.get(
                    SPARQL_ENDPOINT,
                    params={"query": query},
                    headers=headers,
                    timeout=90,
                    proxies=proxies or None,
                    verify=not insecure,
                )
                response.raise_for_status()
                return response.json()

            url = f"{SPARQL_ENDPOINT}?{urlencode({'query': query})}"
            context = ssl._create_unverified_context() if insecure else ssl.create_default_context()
            opener = build_opener(
                ProxyHandler(proxies or {}),
                HTTPSHandler(context=context),
            )
            request = Request(url, headers=headers)
            with opener.open(request, timeout=90) as response:
                return json.load(response)
        except Exception as exc:
            last_error = exc
            if attempt == retries:
                break
            time.sleep(sleep_seconds)

    raise RuntimeError(f"Failed to fetch Wikidata after {retries} attempts") from last_error


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=5000)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument(
        "--class-qid",
        type=str,
        default="Q7397",
        help="Wikidata class QID to expand through instance-of/subclass-of traversal.",
    )
    parser.add_argument(
        "--insecure",
        action="store_true",
        help="Disable TLS certificate verification when a local proxy intercepts HTTPS traffic.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "data/raw/wikidata/wikidata_entities_raw.json",
    )
    args = parser.parse_args()

    payload = fetch_entities(
        args.limit,
        offset=args.offset,
        class_qid=args.class_qid,
        insecure=args.insecure,
    )
    save_json(args.output, payload)
    print(
        f"Saved raw Wikidata results to {args.output} "
        f"(class_qid={args.class_qid}, limit={args.limit}, offset={args.offset}, insecure={args.insecure})"
    )


if __name__ == "__main__":
    main()
