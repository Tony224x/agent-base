from __future__ import annotations

from typing import Protocol


class ExtractClientInfoPort(Protocol):
    """Inbound port for extracting structured client information from a conversation."""

    async def execute(self, conversation_id: str) -> dict: ...
