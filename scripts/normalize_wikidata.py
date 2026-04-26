#!/usr/bin/env python3
"""Normalize raw Wikidata SPARQL results into the project entity schema."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from software_ai_kg.io_utils import load_json, save_json
from software_ai_kg.text_utils import clean_description
from software_ai_kg.wikidata import normalize_wikidata_payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=ROOT / "data/raw/wikidata/demo_wikidata_entities_raw.json",
    )
    parser.add_argument(
        "--rules",
        type=Path,
        default=ROOT / "configs/wikidata_category_rules.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "data/interim/wikidata_entities_normalized.json",
    )
    parser.add_argument(
        "--stats-output",
        type=Path,
        default=ROOT / "outputs/figures/wikidata_normalization_stats.json",
    )
    parser.add_argument("--description-max-chars", type=int, default=50)
    args = parser.parse_args()

    payload = load_json(args.input)
    rules = load_json(args.rules)
    entities, stats = normalize_wikidata_payload(payload, rules)

    for entity in entities:
        entity.description = clean_description(entity.description, max_chars=args.description_max_chars)

    save_json(args.output, [entity.to_dict() for entity in entities])
    save_json(args.stats_output, stats)
    print(
        f"Saved normalized Wikidata entities to {args.output} "
        f"(kept={stats['kept_records']}, dropped={stats['dropped_records']})"
    )


if __name__ == "__main__":
    main()
