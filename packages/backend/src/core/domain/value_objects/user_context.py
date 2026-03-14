from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class UserContext:
    user_id: str
    tenant_id: str | None = None
    roles: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
