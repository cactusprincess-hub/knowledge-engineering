from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EntityRecord:
    id: str
    entity: str
    category: str
    description: str
    source: list[str] = field(default_factory=list)
    level: str = "3"
    aliases: list[str] = field(default_factory=list)
    extra: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: dict) -> "EntityRecord":
        source = payload.get("source", [])
        if isinstance(source, str):
            source = [source]
        return cls(
            id=str(payload.get("id", "")),
            entity=payload["entity"],
            category=payload["category"],
            description=payload.get("description", ""),
            source=source,
            level=str(payload.get("level", "3")),
            aliases=payload.get("aliases", []),
            extra=payload.get("extra", {}),
        )

    def to_dict(self) -> dict:
        payload = {
            "id": self.id,
            "entity": self.entity,
            "category": self.category,
            "description": self.description,
            "source": self.source,
            "level": self.level,
        }
        if self.aliases:
            payload["aliases"] = self.aliases
        if self.extra:
            payload["extra"] = self.extra
        return payload
