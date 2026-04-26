#!/usr/bin/env python3
"""Normalize and deduplicate all persisted Wikidata batch files."""

from __future__ import annotations

import argparse
from collections import Counter
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
        "--input-dir",
        type=Path,
        default=ROOT / "data/raw/wikidata/batches",
    )
    parser.add_argument(
        "--rules",
        type=Path,
        default=ROOT / "configs/wikidata_category_rules.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "data/interim/wikidata_entities_normalized_from_batches.json",
    )
    parser.add_argument(
        "--stats-output",
        type=Path,
        default=ROOT / "outputs/figures/wikidata_scale_normalization_stats.json",
    )
    parser.add_argument("--description-max-chars", type=int, default=50)
    args = parser.parse_args()

    rules = load_json(args.rules)
    batch_files = sorted(args.input_dir.glob("*.json"))
    combined_entities = []
    combined_stats = Counter()
    category_counter: Counter[str] = Counter()
    per_file = []

    for path in batch_files:
        payload = load_json(path)
        entities, stats = normalize_wikidata_payload(payload, rules)
        for entity in entities:
            entity.description = clean_description(entity.description, max_chars=args.description_max_chars)
            combined_entities.append(entity)
            category_counter[entity.category] += 1

        combined_stats["raw_records"] += stats["raw_records"]
        combined_stats["kept_records"] += stats["kept_records"]
        combined_stats["dropped_records"] += stats["dropped_records"]
        combined_stats["missing_description_fallbacks"] += stats["missing_description_fallbacks"]
        combined_stats["dropped_generic_description"] += stats.get("dropped_generic_description", 0)
        per_file.append(
            {
                "file": str(path),
                "raw_records": stats["raw_records"],
                "kept_records": stats["kept_records"],
                "dropped_records": stats["dropped_records"],
            }
        )

    deduped = []
    seen_ids = set()
    duplicate_count = 0
    for entity in combined_entities:
        if entity.id in seen_ids:
            duplicate_count += 1
            continue
        seen_ids.add(entity.id)
        deduped.append(entity)

    save_json(args.output, [entity.to_dict() for entity in deduped])
    save_json(
        args.stats_output,
        {
            "batch_file_count": len(batch_files),
            "raw_records": combined_stats["raw_records"],
            "normalized_records_before_dedup": combined_stats["kept_records"],
            "deduplicated_records": len(deduped),
            "duplicate_records_removed": duplicate_count,
            "dropped_records": combined_stats["dropped_records"],
            "missing_description_fallbacks": combined_stats["missing_description_fallbacks"],
            "dropped_generic_description": combined_stats["dropped_generic_description"],
            "category_breakdown": dict(sorted(category_counter.items())),
            "files": per_file,
        },
    )
    print(
        f"Saved normalized batch entities to {args.output} "
        f"(deduplicated_records={len(deduped)}, duplicates_removed={duplicate_count})"
    )


if __name__ == "__main__":
    main()
