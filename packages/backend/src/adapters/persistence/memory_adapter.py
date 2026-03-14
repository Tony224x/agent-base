from __future__ import annotations

from src.domain.models.conversation import Conversation


class InMemoryPersistenceAdapter:
    """In-memory persistence adapter for development and testing."""

    def __init__(self) -> None:
        self._conversations: dict[str, Conversation] = {}
        self._graph_states: dict[str, dict] = {}

    async def save_conversation(self, conversation: Conversation) -> None:
        self._conversations[conversation.id] = conversation

    async def load_conversation(self, conversation_id: str) -> Conversation | None:
        return self._conversations.get(conversation_id)

    async def list_conversations(self, user_id: str) -> list[Conversation]:
        return [
            c for c in self._conversations.values()
            if c.user_id == user_id
        ]

    async def delete_conversation(self, conversation_id: str) -> bool:
        if conversation_id in self._conversations:
            del self._conversations[conversation_id]
            self._graph_states.pop(conversation_id, None)
            return True
        return False

    async def save_graph_state(self, conversation_id: str, state: dict) -> None:
        self._graph_states[conversation_id] = state

    async def load_graph_state(self, conversation_id: str) -> dict | None:
        return self._graph_states.get(conversation_id)
