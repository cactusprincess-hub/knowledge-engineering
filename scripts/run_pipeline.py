#!/usr/bin/env python3
"""运行示例数据处理流程。"""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from software_ai_kg.alignment import count_sources
from software_ai_kg.frontier_ai import titles_to_entities
from software_ai_kg.io_utils import load_json, save_json
from software_ai_kg.models import EntityRecord
from software_ai_kg.qc import filter_entities
from software_ai_kg.taxonomy import assign_single_parent, remove_cycle_edges
from software_ai_kg.text_utils import clean_description

def main() -> None:
    taxonomy_config = load_json(ROOT / "configs/taxonomy.json")

    titles = load_json(ROOT / "data/raw/frontier_ai/demo_titles.json")
    frontier_entities = titles_to_entities(titles)
    save_json(ROOT / "data/interim/frontier_ai_entities.json", frontier_entities)

    subclass_edges = load_json(ROOT / "data/raw/wikidata/demo_subclass_edges.json")
    acyclic_edges, removed_cycles = remove_cycle_edges(subclass_edges)
    tree_edges, dropped_multi_parent = assign_single_parent(
        acyclic_edges,
        preferred_parents=taxonomy_config["preferred_parents"],
    )
    save_json(
        ROOT / "data/interim/taxonomy_tree.json",
        {
            "root": taxonomy_config["root"],
            "removed_cycle_edges": removed_cycles,
            "dropped_multi_parent_edges": dropped_multi_parent,
            "tree_edges": tree_edges,
        },
    )

    raw_records = []
    for path in (
        ROOT / "data/raw/wikidata/demo_entities.json",
        ROOT / "data/raw/baidubaike/demo_entities.json",
    ):
        raw_records.extend(EntityRecord.from_dict(item) for item in load_json(path))
    raw_records.extend(EntityRecord.from_dict(item) for item in frontier_entities)

    cleaned_records = []
    for record in raw_records:
        record.description = clean_description(record.description, max_chars=50)
        cleaned_records.append(record)

    from software_ai_kg.alignment import deduplicate_entities

    merged_records = deduplicate_entities(cleaned_records)
    filtered_records, qc_summary = filter_entities(
        merged_records,
        valid_categories=set(taxonomy_config["valid_leaf_categories"]),
    )

    save_json(
        ROOT / "data/interim/merged_entities.json",
        {
            "entities": [record.to_dict() for record in filtered_records],
            "qc_summary": qc_summary,
        },
    )
    save_json(
        ROOT / "data/final/entities.json",
        [record.to_dict() for record in filtered_records],
    )
    save_json(
        ROOT / "outputs/figures/project_summary.json",
        {
            "raw_entity_count": len(raw_records),
            "deduplicated_entity_count": len(merged_records),
            "final_entity_count": len(filtered_records),
            "removed_cycle_edges": len(removed_cycles),
            "dropped_multi_parent_edges": len(dropped_multi_parent),
            "source_breakdown": count_sources(filtered_records),
            "qc_summary": qc_summary,
        },
    )

    print("Pipeline complete.")
    print(f"Final entities: {len(filtered_records)}")
    print(f"Cycle edges removed: {len(removed_cycles)}")
    print(f"Multi-parent edges dropped: {len(dropped_multi_parent)}")


if __name__ == "__main__":
    main()
