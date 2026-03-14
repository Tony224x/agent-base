from __future__ import annotations

from typing import Protocol

from src.core.domain.entities.conversation import Conversation
from src.core.domain.value_objects.user_context import UserContext


class ManageConversationsPort(Protocol):
    """Inbound port for conversation CRUD operations."""

    async def create_conversation(
        self, agent_id: str, user_context: UserContext
    ) -> Conversation: ...

    async def get_conversation(self, conversation_id: str) -> Conversation | None: ...

    async def delete_conversation(self, conversation_id: str) -> bool: ...

    async def list_conversations(self, user_id: str) -> list[Conversation]: ...
