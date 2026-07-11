from __future__ import annotations

import re
from collections import Counter


GENERIC_PHRASES = {
    "software",
    "application software",
    "computer software",
    "database software",
    "database management system",
    "relational database management system",
}


def has_cjk(text: str) -> bool:
    return re.search(r"[\u4e00-\u9fff]", text) is not None


def is_qid_label(label: str) -> bool:
    return re.fullmatch(r"Q\d+", label.strip()) is not None


def select_description_issues(record: dict, long_threshold: int = 45, short_threshold: int = 12) -> list[str]:
    """识别需要规范化的一句话简介。"""
    description = record.get("description", "").strip()
    raw_description = record.get("extra", {}).get("raw_description", description).strip()
    issues = []

    if is_qid_label(record.get("entity", "")):
        issues.append("qid_label")
    if not has_cjk(description) and (
        is_qid_label(record.get("entity", "")) or len(description) > long_threshold or len(description) < short_threshold
    ):
        issues.append("english_description")
    if len(description) > long_threshold or len(raw_description) > long_threshold:
        issues.append("long_description")
    if len(description) < short_threshold:
        issues.append("short_description")
    if description.lower() in GENERIC_PHRASES or raw_description.lower() in GENERIC_PHRASES:
        issues.append("generic_description")
    if description.endswith(("(", "（")):
        issues.append("truncated_description")
    return issues


def heuristic_summary(record: dict, max_chars: int = 30) -> str:
    """仅根据已有字段生成短定义，不引入来源之外的新事实。"""
    entity = record.get("entity", "").strip()
    category = record.get("category", "").strip()
    description = record.get("extra", {}).get("raw_description") or record.get("description", "")
    description = re.sub(r"\s+", " ", description).strip()

    if has_cjk(description):
        summary = description
    elif category:
        if is_qid_label(entity):
            summary = f"属于{category}类别的软件实体"
        elif "database" in description.lower():
            summary = f"{entity}是一款数据库相关软件"
        elif "programming language" in description.lower():
            summary = f"{entity}是一种编程语言"
        elif "operating system" in description.lower():
            summary = f"{entity}是一款操作系统"
        elif "video game" in description.lower() or category == "图像与视频处理":
            summary = f"{entity}是一款数字内容或游戏软件"
        else:
            summary = f"{entity}是{category}相关软件"
    else:
        summary = description

    summary = re.split(r"[。；;.!！]", summary, maxsplit=1)[0].strip()
    if len(summary) > max_chars:
        summary = summary[:max_chars]
    return summary


def summarize_records(records: list[dict], limit: int = 100, max_chars: int = 30) -> tuple[list[dict], dict]:
    candidates = []
    reason_counter: Counter[str] = Counter()

    for record in records:
        issues = select_description_issues(record)
        if not issues:
            continue
        for issue in issues:
            reason_counter[issue] += 1
        candidates.append((record, issues))

    processed = []
    for record, issues in candidates[:limit]:
        before = record.get("description", "")
        after = heuristic_summary(record, max_chars=max_chars)
        updated = dict(record)
        updated["description"] = after
        extra = dict(updated.get("extra", {}))
        # 保留原始描述和问题标签，便于回溯每条简介的处理原因。
        extra["original_description"] = before
        extra["description_issues"] = issues
        extra["normalization_method"] = "rule_based_description_normalization"
        updated["extra"] = extra
        processed.append(updated)

    stats = {
        "input_records": len(records),
        "candidate_records": len(candidates),
        "processed_records": len(processed),
        "max_summary_chars": max_chars,
        "reason_breakdown": dict(sorted(reason_counter.items())),
        "sample_outputs": processed[:10],
    }
    return processed, stats
