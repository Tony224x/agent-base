from __future__ import annotations

from typing import Protocol


class RetrieverPort(Protocol):
    """Port for document/knowledge retrieval (e.g., vector search)."""

    async def retrieve(self, query: str, top_k: int = 5) -> list[dict]: ...
