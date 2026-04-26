#!/usr/bin/env python3
"""Clean subclass edges into a canonical tree for the course project."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from software_ai_kg.io_utils import load_json, save_json
from software_ai_kg.taxonomy import assign_single_parent, remove_cycle_edges


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
        "--output",
        type=Path,
        default=ROOT / "data/interim/taxonomy_tree.json",
    )
    args = parser.parse_args()

    edges = load_json(args.edges)
    config = load_json(args.config)
    acyclic_edges, removed_cycles = remove_cycle_edges(edges)
    tree_edges, dropped_multi_parent = assign_single_parent(
        acyclic_edges,
        preferred_parents=config.get("preferred_parents", []),
        parent_overrides=config.get("canonical_parent_overrides", {}),
    )

    payload = {
        "root": config["root"],
        "removed_cycle_edges": removed_cycles,
        "dropped_multi_parent_edges": dropped_multi_parent,
        "tree_edges": tree_edges,
    }
    save_json(args.output, payload)
    print(
        f"Saved taxonomy tree to {args.output} "
        f"(removed_cycles={len(removed_cycles)}, dropped_multi_parent={len(dropped_multi_parent)})"
    )


if __name__ == "__main__":
    main()
