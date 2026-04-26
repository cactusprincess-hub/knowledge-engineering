from __future__ import annotations

import re
from collections import Counter
from difflib import SequenceMatcher

try:
    from rapidfuzz import fuzz
except ImportError:  # pragma: no cover - fallback for minimal local environments
    fuzz = None

from software_ai_kg.models import EntityRecord
from software_ai_kg.text_utils import clean_description


def normalize_entity_name(name: str) -> str:
    name = name.strip().lower()
    name = re.sub(r"[\s\-_]+", "", name)
    return name


def _description_score(text: str) -> tuple[int, int]:
    return (len(text), text.count("的"))


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


def deduplicate_entities(records: list[EntityRecord], fuzzy_threshold: int = 95) -> list[EntityRecord]:
    merged: list[EntityRecord] = []
    index_by_key: dict[str, int] = {}

    for record in records:
        keys = {normalize_entity_name(record.entity)}
        keys.update(normalize_entity_name(alias) for alias in record.aliases)

        matched_index = None
        for key in keys:
            if key in index_by_key:
                matched_index = index_by_key[key]
                break

        if matched_index is None:
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
        existing.description = merge_descriptions(existing.description, record.description)
        existing.source = sorted(set(existing.source + record.source))
        existing.aliases = sorted(set(existing.aliases + record.aliases + [record.entity]))
        if not existing.id and record.id:
            existing.id = record.id

    return merged


def count_sources(records: list[EntityRecord]) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for record in records:
        for source in record.source:
            counter[source] += 1
    return dict(sorted(counter.items()))
