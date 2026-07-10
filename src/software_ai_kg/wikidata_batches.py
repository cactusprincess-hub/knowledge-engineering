from __future__ import annotations

from collections import Counter
from pathlib import Path


def build_batch_output_path(output_dir: Path, target_name: str, offset: int) -> Path:
    """Use deterministic filenames so interrupted crawls can resume by batch."""
    filename = f"{target_name}_offset_{offset:05d}.json"
    return output_dir / filename


def build_manifest(
    *,
    target: dict,
    output_path: Path,
    batch_index: int,
    offset: int,
    batch_size: int,
    result_count: int,
    skipped_existing: bool,
    status: str = "success",
    error_message: str = "",
) -> dict:
    """Record one fetch batch for reproducibility and later scale statistics."""
    return {
        "target_name": target["name"],
        "target_qid": target["qid"],
        "target_label": target["label"],
        "suggested_category": target.get("suggested_category", ""),
        "batch_index": batch_index,
        "offset": offset,
        "batch_size": batch_size,
        "result_count": result_count,
        "output_path": str(output_path),
        "skipped_existing": skipped_existing,
        "status": status,
        "error_message": error_message,
    }


def summarise_manifest(entries: list[dict]) -> dict:
    """Aggregate batch-level fetch metadata into report-ready counts."""
    raw_record_count = sum(entry["result_count"] for entry in entries)
    target_counter: Counter[str] = Counter()
    batch_counter: Counter[str] = Counter()
    skipped_existing = 0
    failed_batch_count = 0

    for entry in entries:
        target_counter[entry["target_name"]] += entry["result_count"]
        batch_counter[entry["target_name"]] += 1
        if entry["skipped_existing"]:
            skipped_existing += 1
        if entry.get("status") != "success":
            failed_batch_count += 1

    return {
        "batch_file_count": len(entries),
        "raw_record_count": raw_record_count,
        "skipped_existing_batch_count": skipped_existing,
        "failed_batch_count": failed_batch_count,
        "records_by_target": dict(sorted(target_counter.items())),
        "batches_by_target": dict(sorted(batch_counter.items())),
    }
