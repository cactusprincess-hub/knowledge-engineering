#!/usr/bin/env python3
"""Create standardized description summaries for noisy entity records."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from software_ai_kg.io_utils import load_json, save_json
from software_ai_kg.summary_qc import summarize_records


def load_entity_list(path: Path) -> list[dict]:
    payload = load_json(path)
    if isinstance(payload, dict) and "entities" in payload:
        return payload["entities"]
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=ROOT / "data/interim/wikidata_entities_normalized_from_batches.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "data/interim/description_qc_sample.json",
    )
    parser.add_argument(
        "--stats-output",
        type=Path,
        default=ROOT / "outputs/figures/description_qc_stats.json",
    )
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--max-chars", type=int, default=30)
    args = parser.parse_args()

    records = load_entity_list(args.input)
    processed, stats = summarize_records(records, limit=args.limit, max_chars=args.max_chars)
    save_json(args.output, processed)
    save_json(args.stats_output, stats)
    print(
        f"Saved description summaries to {args.output} "
        f"(candidates={stats['candidate_records']}, processed={stats['processed_records']})"
    )


if __name__ == "__main__":
    main()
