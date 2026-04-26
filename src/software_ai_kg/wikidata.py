from __future__ import annotations

from collections import Counter
import re

from software_ai_kg.models import EntityRecord


NON_SOFTWARE_HINTS = (
    "company",
    "business",
    "organization",
    "human",
    "person",
    "university",
    "country",
)


def _binding_text(binding: dict, key: str) -> str:
    value = binding.get(key, {})
    if isinstance(value, dict):
        return str(value.get("value", "")).strip()
    return ""


def _extract_qid(uri: str) -> str:
    match = re.search(r"/(Q\d+)$", uri)
    return match.group(1) if match else uri


def _normalize_text(text: str) -> str:
    return text.strip().lower()


def _keyword_matches(haystack: str, keyword: str) -> bool:
    normalized = _normalize_text(keyword)
    if not normalized:
        return False
    if re.fullmatch(r"[a-z0-9\- ]+", normalized):
        pattern = r"(?<![a-z0-9])" + re.escape(normalized) + r"(?![a-z0-9])"
        return re.search(pattern, haystack) is not None
    return normalized in haystack


def infer_category(item_label: str, instance_label: str, description: str, rules_config: dict) -> str:
    haystack = " ".join(
        _normalize_text(part)
        for part in (item_label, instance_label, description)
        if part
    )
    for rule in rules_config.get("rules", []):
        for keyword in rule.get("keywords", []):
            if _keyword_matches(haystack, keyword):
                return rule["category"]
    return rules_config.get("default_category", "开发库与SDK")


def _looks_like_non_software(instance_label: str, description: str) -> bool:
    haystack = " ".join((_normalize_text(instance_label), _normalize_text(description)))
    return any(keyword in haystack for keyword in NON_SOFTWARE_HINTS)


def normalize_wikidata_payload(payload: dict, rules_config: dict) -> tuple[list[EntityRecord], dict]:
    bindings = payload.get("results", {}).get("bindings", [])
    entities: list[EntityRecord] = []
    dropped_records = 0
    missing_description = 0
    category_counter: Counter[str] = Counter()

    for binding in bindings:
        item_uri = _binding_text(binding, "item")
        item_label = _binding_text(binding, "itemLabel")
        instance_uri = _binding_text(binding, "instance")
        instance_label = _binding_text(binding, "instanceLabel")
        description = _binding_text(binding, "description")

        if not item_uri or not item_label:
            dropped_records += 1
            continue
        if _looks_like_non_software(instance_label, description):
            dropped_records += 1
            continue
        if not description:
            missing_description += 1
            description = instance_label or "Wikidata software entity without description"

        category = infer_category(item_label, instance_label, description, rules_config)
        category_counter[category] += 1
        entities.append(
            EntityRecord(
                id=_extract_qid(item_uri),
                entity=item_label,
                category=category,
                description=description,
                source=["Wikidata"],
                level="3",
                extra={
                    "instance_id": _extract_qid(instance_uri) if instance_uri else "",
                    "instance_label": instance_label,
                    "raw_description": description,
                },
            )
        )

    stats = {
        "raw_records": len(bindings),
        "kept_records": len(entities),
        "dropped_records": dropped_records,
        "missing_description_fallbacks": missing_description,
        "category_breakdown": dict(sorted(category_counter.items())),
    }
    return entities, stats
