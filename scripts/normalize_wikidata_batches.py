#!/usr/bin/env python3
"""规范化并去重已保存的 Wikidata 批量抓取文件。"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from software_ai_kg.io_utils import load_json, save_json
from software_ai_kg.text_utils import clean_description
from software_ai_kg.wikidata import normalize_wikidata_payload


def target_name_from_path(path: Path) -> str:
    stem = path.stem
    return stem.rsplit("_offset_", 1)[0]


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
    parser.add_argument("--short-description-threshold", type=int, default=12)
    args = parser.parse_args()

    rules = load_json(args.rules)
    batch_files = sorted(args.input_dir.glob("*.json"))
    combined_entities = []
    combined_stats = Counter()
    category_counter: Counter[str] = Counter()
    per_file = []
    entity_targets: dict[str, set[str]] = defaultdict(set)
    entity_categories: dict[str, set[str]] = defaultdict(set)
    short_description_count = 0

    for path in batch_files:
        payload = load_json(path)
        entities, stats = normalize_wikidata_payload(payload, rules)
        target_name = target_name_from_path(path)
        for entity in entities:
            entity.description = clean_description(entity.description, max_chars=args.description_max_chars)
            combined_entities.append(entity)
            category_counter[entity.category] += 1
            entity_targets[entity.id].add(target_name)
            entity_categories[entity.id].add(entity.category)
            if len(entity.description) < args.short_description_threshold:
                short_description_count += 1

        combined_stats["raw_records"] += stats["raw_records"]
        combined_stats["kept_records"] += stats["kept_records"]
        combined_stats["dropped_records"] += stats["dropped_records"]
        combined_stats["dropped_missing_identity"] += stats.get("dropped_missing_identity", 0)
        combined_stats["dropped_non_software"] += stats.get("dropped_non_software", 0)
        combined_stats["missing_description_fallbacks"] += stats["missing_description_fallbacks"]
        combined_stats["dropped_generic_description"] += stats.get("dropped_generic_description", 0)
        per_file.append(
            {
                "file": str(path),
                "target_name": target_name,
                "raw_records": stats["raw_records"],
                "kept_records": stats["kept_records"],
                "dropped_records": stats["dropped_records"],
            }
        )

    deduped = []
    deduped_by_id = {}
    duplicate_count = 0
    for entity in combined_entities:
        if entity.id in deduped_by_id:
            duplicate_count += 1
            existing = deduped_by_id[entity.id]
            merged_targets = sorted(entity_targets[entity.id])
            merged_categories = sorted(entity_categories[entity.id])
            existing.extra["batch_targets"] = merged_targets
            if len(merged_categories) > 1:
                existing.extra["overlap_categories"] = merged_categories
            continue
        entity.extra["batch_targets"] = sorted(entity_targets[entity.id])
        if len(entity_categories[entity.id]) > 1:
            entity.extra["overlap_categories"] = sorted(entity_categories[entity.id])
        deduped_by_id[entity.id] = entity
        deduped.append(entity)

    overlap_examples = []
    overlap_entity_count = 0
    cross_category_overlap_count = 0
    for entity in deduped:
        targets = entity.extra.get("batch_targets", [])
        if len(targets) > 1:
            overlap_entity_count += 1
            if len(overlap_examples) < 10:
                overlap_examples.append(
                    {
                        "id": entity.id,
                        "entity": entity.entity,
                        "targets": targets,
                        "categories": entity.extra.get("overlap_categories", [entity.category]),
                    }
                )
        if len(entity.extra.get("overlap_categories", [])) > 1:
            cross_category_overlap_count += 1

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
            "dropped_missing_identity": combined_stats["dropped_missing_identity"],
            "dropped_non_software": combined_stats["dropped_non_software"],
            "missing_description_fallbacks": combined_stats["missing_description_fallbacks"],
            "dropped_generic_description": combined_stats["dropped_generic_description"],
            "short_description_threshold": args.short_description_threshold,
            "short_description_count": short_description_count,
            "short_description_ratio": round(short_description_count / max(len(combined_entities), 1), 4),
            "drop_ratio": round(combined_stats["dropped_records"] / max(combined_stats["raw_records"], 1), 4),
            "overlap_entity_count": overlap_entity_count,
            "cross_category_overlap_count": cross_category_overlap_count,
            "overlap_examples": overlap_examples,
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
