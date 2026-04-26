from __future__ import annotations

from software_ai_kg.models import EntityRecord


def filter_entities(
    records: list[EntityRecord],
    valid_categories: set[str],
) -> tuple[list[EntityRecord], dict]:
    kept: list[EntityRecord] = []
    dropped_category = 0
    dropped_description = 0

    for record in records:
        if record.category not in valid_categories:
            dropped_category += 1
            continue
        if not record.description or len(record.description) < 6:
            dropped_description += 1
            continue
        kept.append(record)

    summary = {
        "kept": len(kept),
        "dropped_invalid_category": dropped_category,
        "dropped_bad_description": dropped_description,
    }
    return kept, summary
