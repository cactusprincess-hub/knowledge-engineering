#!/usr/bin/env python3
"""Fetch software-related entities from Wikidata via SPARQL."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import requests

from software_ai_kg.io_utils import save_json

SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"

SOFTWARE_QUERY = """
SELECT ?item ?itemLabel ?instanceLabel ?description WHERE {
  ?item wdt:P31/wdt:P279* wd:Q7397.
  OPTIONAL { ?item schema:description ?description FILTER(LANG(?description) = "en") }
  OPTIONAL { ?item wdt:P31 ?instance . }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en,zh". }
}
LIMIT {limit}
""".strip()


def fetch_entities(limit: int) -> dict:
    query = SOFTWARE_QUERY.format(limit=limit)
    headers = {
        "Accept": "application/sparql-results+json",
        "User-Agent": "software-ai-kg-course-project/0.1"
    }
    response = requests.get(
        SPARQL_ENDPOINT,
        params={"query": query},
        headers=headers,
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=5000)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "data/raw/wikidata/wikidata_entities_raw.json",
    )
    args = parser.parse_args()

    payload = fetch_entities(args.limit)
    save_json(args.output, payload)
    print(f"Saved raw Wikidata results to {args.output}")


if __name__ == "__main__":
    main()
