from __future__ import annotations

from src.core.ports.outbound.conversation_repository import PersistencePort


class ExtractClientInfoUseCase:
    """Use case: Extract structured client information from conversation context.

    Skeleton — raises NotImplementedError until extraction logic is implemented.
    """

    def __init__(self, persistence: PersistencePort) -> None:
        self._persistence = persistence

    async def execute(self, conversation_id: str) -> dict:
        raise NotImplementedError(
            "Client info extraction is not yet implemented"
        )
