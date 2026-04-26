#!/usr/bin/env python3
"""Fetch Wikidata entities in balanced category batches and persist a manifest."""

from __future__ import annotations

import argparse
from datetime import datetime, UTC
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from software_ai_kg.io_utils import load_json, save_json
from software_ai_kg.wikidata_batches import (
    build_batch_output_path,
    build_manifest,
    summarise_manifest,
)

import fetch_wikidata


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs/wikidata_batch_targets.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "data/raw/wikidata/batches",
    )
    parser.add_argument(
        "--manifest-output",
        type=Path,
        default=ROOT / "outputs/figures/wikidata_batch_manifest.json",
    )
    parser.add_argument(
        "--stats-output",
        type=Path,
        default=ROOT / "outputs/figures/wikidata_scale_stats.json",
    )
    parser.add_argument("--batch-size", type=int, default=None)
    parser.add_argument("--max-batches", type=int, default=None)
    parser.add_argument("--sleep-seconds", type=float, default=None)
    parser.add_argument("--only-target", type=str, default=None)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--insecure", action="store_true")
    args = parser.parse_args()

    config = load_json(args.config)
    batch_size = args.batch_size or config.get("batch_size", 100)
    max_batches = args.max_batches or config.get("max_batches_per_target", 10)
    sleep_seconds = args.sleep_seconds if args.sleep_seconds is not None else config.get("sleep_seconds", 1)

    manifest_entries: list[dict] = []
    for target in config.get("targets", []):
        if args.only_target and target["name"] != args.only_target:
            continue

        for batch_index in range(max_batches):
            offset = batch_index * batch_size
            output_path = build_batch_output_path(args.output_dir, target["name"], offset)

            if output_path.exists() and not args.overwrite:
                payload = load_json(output_path)
                result_count = len(payload.get("results", {}).get("bindings", []))
                manifest_entries.append(
                    build_manifest(
                        target=target,
                        output_path=output_path,
                        batch_index=batch_index,
                        offset=offset,
                        batch_size=batch_size,
                        result_count=result_count,
                        skipped_existing=True,
                    )
                )
                continue

            payload = fetch_wikidata.fetch_entities(
                limit=batch_size,
                offset=offset,
                class_qid=target["qid"],
                insecure=args.insecure,
            )
            save_json(output_path, payload)
            result_count = len(payload.get("results", {}).get("bindings", []))
            manifest_entries.append(
                build_manifest(
                    target=target,
                    output_path=output_path,
                    batch_index=batch_index,
                    offset=offset,
                    batch_size=batch_size,
                    result_count=result_count,
                    skipped_existing=False,
                )
            )

            if result_count < batch_size:
                break
            time.sleep(sleep_seconds)

    summary = summarise_manifest(manifest_entries)
    manifest_payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "batch_size": batch_size,
        "max_batches_requested": max_batches,
        "entries": manifest_entries,
        "summary": summary,
    }
    save_json(args.manifest_output, manifest_payload)
    save_json(args.stats_output, summary)
    print(
        f"Saved batch manifest to {args.manifest_output} "
        f"(files={summary['batch_file_count']}, raw_records={summary['raw_record_count']})"
    )


if __name__ == "__main__":
    main()
