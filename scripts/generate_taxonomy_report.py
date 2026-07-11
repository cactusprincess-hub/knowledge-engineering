#!/usr/bin/env python3
"""生成报告可引用的本体治理结果。"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from software_ai_kg.io_utils import load_json, save_json
from software_ai_kg.taxonomy import assign_single_parent, build_tree_lines, remove_cycle_edges


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--edges",
        type=Path,
        default=ROOT / "data/raw/wikidata/demo_subclass_edges.json",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs/taxonomy.json",
    )
    parser.add_argument(
        "--report-output",
        type=Path,
        default=ROOT / "outputs/figures/taxonomy_governance_report.json",
    )
    parser.add_argument(
        "--tree-output",
        type=Path,
        default=ROOT / "outputs/figures/taxonomy_tree.txt",
    )
    args = parser.parse_args()

    edges = load_json(args.edges)
    config = load_json(args.config)

    acyclic_edges, removed_cycles = remove_cycle_edges(edges, include_metadata=True)
    tree_edges, dropped_multi_parent = assign_single_parent(
        acyclic_edges,
        preferred_parents=config.get("preferred_parents", []),
        parent_overrides=config.get("canonical_parent_overrides", {}),
        include_metadata=True,
    )

    tree_text = "\n".join(build_tree_lines(config["root"], tree_edges))
    args.tree_output.parent.mkdir(parents=True, exist_ok=True)
    args.tree_output.write_text(tree_text, encoding="utf-8")

    canonical_override_count = sum(
        1 for edge in tree_edges if edge.get("selection_reason") == "canonical_override"
    )
    report = {
        "root": config["root"],
        "raw_edge_count": len(edges),
        "acyclic_edge_count": len(acyclic_edges),
        "tree_edge_count": len(tree_edges),
        "cycle_edge_count": len(removed_cycles),
        "multi_parent_pruned_edge_count": len(dropped_multi_parent),
        "canonical_override_count": canonical_override_count,
        "cycle_examples": removed_cycles[:10],
        "multi_parent_examples": dropped_multi_parent[:10],
        "tree_preview": build_tree_lines(config["root"], tree_edges)[:40],
    }
    save_json(args.report_output, report)
    print(
        f"Saved taxonomy governance report to {args.report_output} "
        f"(cycles={report['cycle_edge_count']}, multi_parent_pruned={report['multi_parent_pruned_edge_count']})"
    )


if __name__ == "__main__":
    main()
