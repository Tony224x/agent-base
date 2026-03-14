from __future__ import annotations

from src.core.domain.entities.conversation import Conversation
from src.core.domain.value_objects.user_context import UserContext
from src.core.ports.outbound.conversation_repository import PersistencePort


class ManageConversationsUseCase:
    """Use case: CRUD operations on conversations via the persistence port."""

    def __init__(self, persistence: PersistencePort) -> None:
        self._persistence = persistence

    async def create_conversation(
        self, agent_id: str, user_context: UserContext
    ) -> Conversation:
        conversation = Conversation(
            agent_id=agent_id,
            user_id=user_context.user_id,
        )
        await self._persistence.save_conversation(conversation)
        return conversation

    async def get_conversation(self, conversation_id: str) -> Conversation | None:
        return await self._persistence.load_conversation(conversation_id)

    async def delete_conversation(self, conversation_id: str) -> bool:
        return await self._persistence.delete_conversation(conversation_id)

    async def list_conversations(self, user_id: str) -> list[Conversation]:
        return await self._persistence.list_conversations(user_id)
