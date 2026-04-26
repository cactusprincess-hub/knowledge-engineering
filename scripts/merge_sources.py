#!/usr/bin/env python3
"""Merge, clean, and deduplicate entities from all sources."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from software_ai_kg.alignment import deduplicate_entities
from software_ai_kg.io_utils import load_json, save_json
from software_ai_kg.models import EntityRecord
from software_ai_kg.qc import filter_entities
from software_ai_kg.text_utils import clean_description


def load_records(path: Path) -> list[EntityRecord]:
    return [EntityRecord.from_dict(item) for item in load_json(path)]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--wikidata",
        type=Path,
        default=ROOT / "data/raw/wikidata/demo_entities.json",
    )
    parser.add_argument(
        "--baike",
        type=Path,
        default=ROOT / "data/raw/baidubaike/demo_entities.json",
    )
    parser.add_argument(
        "--frontier",
        type=Path,
        default=ROOT / "data/interim/frontier_ai_entities.json",
    )
    parser.add_argument(
        "--taxonomy",
        type=Path,
        default=ROOT / "configs/taxonomy.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "data/interim/merged_entities.json",
    )
    args = parser.parse_args()

    records = []
    for path in (args.wikidata, args.baike, args.frontier):
        records.extend(load_records(path))

    for record in records:
        record.description = clean_description(record.description, max_chars=50)

    merged = deduplicate_entities(records)
    taxonomy = load_json(args.taxonomy)
    filtered, qc_summary = filter_entities(
        merged,
        valid_categories=set(taxonomy["valid_leaf_categories"]),
    )

    payload = {
        "entities": [record.to_dict() for record in filtered],
        "qc_summary": qc_summary,
    }
    save_json(args.output, payload)
    print(
        f"Saved merged entities to {args.output} "
        f"(kept={len(filtered)}, dropped={len(merged) - len(filtered)})"
    )


if __name__ == "__main__":
    main()
