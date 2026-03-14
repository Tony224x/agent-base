from __future__ import annotations

from typing import Protocol, AsyncIterator

from src.domain.models.conversation import Message


class LLMPort(Protocol):
    async def chat(self, messages: list[Message], model: str) -> Message: ...
    async def stream(self, messages: list[Message], model: str) -> AsyncIterator[str]: ...
