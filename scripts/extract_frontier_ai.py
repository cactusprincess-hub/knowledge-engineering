#!/usr/bin/env python3
"""Extract frontier AI entities from titles or headlines."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from software_ai_kg.frontier_ai import titles_to_entities
from software_ai_kg.io_utils import load_json, save_json


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=ROOT / "data/raw/frontier_ai/demo_titles.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "data/interim/frontier_ai_entities.json",
    )
    args = parser.parse_args()

    titles = load_json(args.input)
    entities = titles_to_entities(titles)
    save_json(args.output, entities)
    print(f"Saved extracted frontier AI entities to {args.output}")


if __name__ == "__main__":
    main()
