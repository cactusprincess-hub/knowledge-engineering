from __future__ import annotations

import re


DESCRIPTION_HINTS = {
    "DeepSeek-R1": ("大语言模型", "由深度求索推出的推理增强型大语言模型"),
    "Sora": ("扩散与生成模型", "由OpenAI提出的文本生成视频基础模型"),
    "Agentic Workflow": ("智能体工作流", "强调多步骤规划与执行的智能体协同工作范式"),
}


def extract_entity_name(title: str) -> str | None:
    for hint in DESCRIPTION_HINTS:
        if hint.lower() in title.lower():
            return hint

    for separator in (":", " - ", " — "):
        if separator in title:
            candidate = title.split(separator, 1)[0].strip()
            if candidate:
                return candidate

    match = re.match(r"([A-Z][A-Za-z0-9\- ]{2,40})", title)
    if match:
        return match.group(1).strip()
    return None


def titles_to_entities(items: list[dict]) -> list[dict]:
    entities: list[dict] = []
    for idx, item in enumerate(items, start=1):
        name = extract_entity_name(item["title"])
        if not name:
            continue
        category, description = DESCRIPTION_HINTS.get(
            name,
            ("智能助手", "来自新闻或论文标题的前沿AI实体，待进一步校验与补充"),
        )
        entities.append(
            {
                "id": f"F{idx:04d}",
                "entity": name,
                "category": category,
                "description": description,
                "source": item["source"],
                "level": "3",
                "extra": {"raw_title": item["title"]},
            }
        )
    return entities
