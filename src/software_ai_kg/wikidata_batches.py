from __future__ import annotations

from collections import Counter
from pathlib import Path


def build_batch_output_path(output_dir: Path, target_name: str, offset: int) -> Path:
    """使用稳定文件名保存批次，便于抓取中断后继续运行。"""
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
    """记录单个抓取批次，支撑复现和规模统计。"""
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
    """将批次级元数据汇总为报告可引用的统计结果。"""
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
