from __future__ import annotations

from typing import Protocol

from src.core.domain.value_objects.user_context import UserContext


class AuthPort(Protocol):
    async def validate_token(self, token: str) -> UserContext | None: ...
