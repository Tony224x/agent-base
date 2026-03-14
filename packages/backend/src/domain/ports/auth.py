from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass
class UserContext:
    user_id: str
    tenant_id: str | None = None
    roles: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


class AuthPort(Protocol):
    async def validate_token(self, token: str) -> UserContext | None: ...
