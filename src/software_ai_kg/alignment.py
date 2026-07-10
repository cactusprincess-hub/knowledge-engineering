from __future__ import annotations

import re
from collections import Counter
from difflib import SequenceMatcher

try:
    from rapidfuzz import fuzz
except ImportError:
    fuzz = None

from software_ai_kg.models import EntityRecord
from software_ai_kg.text_utils import clean_description


def normalize_entity_name(name: str) -> str:
    name = name.strip().lower()
    name = re.sub(r"[\s\-_]+", "", name)
    return name


def build_alias_index(alias_groups: list[dict]) -> dict[str, list[str]]:
    index: dict[str, list[str]] = {}
    for group in alias_groups:
        # Put all aliases in the same bucket so Chinese and English names can
        # be matched before the more expensive fuzzy comparison step.
        aliases = sorted(set(group.get("aliases", []) + [group.get("canonical", "")]))
        aliases = [alias for alias in aliases if alias]
        for alias in aliases:
            index[normalize_entity_name(alias)] = aliases
    return index


def apply_alias_groups(records: list[EntityRecord], alias_groups: list[dict]) -> list[EntityRecord]:
    alias_index = build_alias_index(alias_groups)
    for record in records:
        keys = {normalize_entity_name(record.entity)}
        keys.update(normalize_entity_name(alias) for alias in record.aliases)
        matched_aliases = []
        for key in keys:
            matched_aliases.extend(alias_index.get(key, []))
        if matched_aliases:
            record.aliases = sorted(set(record.aliases + matched_aliases))
    return records


def _description_score(text: str) -> tuple[int, int, int]:
    """Prefer Chinese descriptions, then richer descriptions, during fusion."""
    cjk_count = len(re.findall(r"[\u4e00-\u9fff]", text))
    return (1 if cjk_count else 0, cjk_count, len(text))


def merge_descriptions(left: str, right: str, max_chars: int = 50) -> str:
    candidates = [item for item in (left, right) if item]
    if not candidates:
        return ""
    best = max(candidates, key=_description_score)
    if len(candidates) == 2 and left != right:
        combo = f"{left}；{right}"
        if len(combo) <= max_chars:
            return combo
    return clean_description(best, max_chars=max_chars)


def deduplicate_entities_with_stats(
    records: list[EntityRecord],
    fuzzy_threshold: int = 95,
) -> tuple[list[EntityRecord], dict]:
    merged: list[EntityRecord] = []
    index_by_key: dict[str, int] = {}
    aligned_examples = []

    for record in records:
        keys = {normalize_entity_name(record.entity)}
        keys.update(normalize_entity_name(alias) for alias in record.aliases)

        matched_index = None
        for key in keys:
            if key in index_by_key:
                matched_index = index_by_key[key]
                break

        if matched_index is None:
            # Alias lookup catches explicit pairs such as WeChat/微信. Fuzzy
            # matching is only used as a fallback and is restricted by category.
            for existing_index, existing in enumerate(merged):
                left = normalize_entity_name(existing.entity)
                right = normalize_entity_name(record.entity)
                if fuzz is not None:
                    score = fuzz.ratio(left, right)
                else:
                    score = SequenceMatcher(None, left, right).ratio() * 100
                if score >= fuzzy_threshold and existing.category == record.category:
                    matched_index = existing_index
                    break

        if matched_index is None:
            merged.append(record)
            for key in keys:
                index_by_key[key] = len(merged) - 1
            continue

        existing = merged[matched_index]
        previous_sources = set(existing.source)
        # Keep a single entity node while preserving all sources and aliases.
        existing.description = merge_descriptions(existing.description, record.description)
        existing.source = sorted(set(existing.source + record.source))
        existing.aliases = sorted(set(existing.aliases + record.aliases + [record.entity]))
        if not existing.id and record.id:
            existing.id = record.id
        if previous_sources != set(existing.source) and len(aligned_examples) < 20:
            aligned_examples.append(
                {
                    "entity": existing.entity,
                    "matched_entity": record.entity,
                    "sources": existing.source,
                    "aliases": existing.aliases[:10],
                }
            )

    multi_source = [record for record in merged if len(record.source) > 1]
    stats = {
        "input_records": len(records),
        "deduplicated_records": len(merged),
        "duplicate_records_removed": len(records) - len(merged),
        "multi_source_entity_count": len(multi_source),
        "aligned_examples": aligned_examples,
    }
    return merged, stats


def deduplicate_entities(records: list[EntityRecord], fuzzy_threshold: int = 95) -> list[EntityRecord]:
    merged, _ = deduplicate_entities_with_stats(records, fuzzy_threshold=fuzzy_threshold)
    return merged


def count_sources(records: list[EntityRecord]) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for record in records:
        for source in record.source:
            counter[source] += 1
    return dict(sorted(counter.items()))
