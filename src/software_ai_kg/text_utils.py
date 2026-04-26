from __future__ import annotations

import re

NOISE_PATTERNS = [
    r"百度百科.*",
    r"编辑.*",
    r"播报.*",
    r"锁定.*",
    r"参考资料.*",
]


def clean_description(text: str, max_chars: int = 50) -> str:
    cleaned = text.strip()
    cleaned = re.sub(r"\[[^\]]+\]", "", cleaned)
    cleaned = re.sub(r"\([^)]*来源[^)]*\)", "", cleaned)
    for pattern in NOISE_PATTERNS:
        cleaned = re.sub(pattern, "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    for separator in ("。", "；", ";", ".", "！", "!", "，", ","):
        if separator in cleaned:
            cleaned = cleaned.split(separator, 1)[0]
            break

    if len(cleaned) > max_chars:
        cleaned = cleaned[:max_chars]
    return cleaned
