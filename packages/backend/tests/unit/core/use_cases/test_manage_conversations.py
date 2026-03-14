from __future__ import annotations

import pytest

from src.core.domain.entities.conversation import Conversation
from src.core.domain.value_objects.user_context import UserContext
from src.core.use_cases.manage_conversations import ManageConversationsUseCase


class FakePersistence:
    """Minimal in-memory fake satisfying PersistencePort."""

    def __init__(self) -> None:
        self._store: dict[str, Conversation] = {}

    async def save_conversation(self, conversation: Conversation) -> None:
        self._store[conversation.id] = conversation

    async def load_conversation(self, conversation_id: str) -> Conversation | None:
        return self._store.get(conversation_id)

    async def list_conversations(self, user_id: str) -> list[Conversation]:
        return [c for c in self._store.values() if c.user_id == user_id]

    async def delete_conversation(self, conversation_id: str) -> bool:
        return self._store.pop(conversation_id, None) is not None

    async def save_graph_state(self, conversation_id: str, state: dict) -> None:
        pass

    async def load_graph_state(self, conversation_id: str) -> dict | None:
        return None


@pytest.fixture
def persistence():
    return FakePersistence()


@pytest.fixture
def use_case(persistence):
    return ManageConversationsUseCase(persistence=persistence)


@pytest.fixture
def user_context():
    return UserContext(user_id="user-1", tenant_id="tenant-1")


@pytest.mark.asyncio
async def test_create_conversation(use_case, user_context):
    conv = await use_case.create_conversation("agent-1", user_context)
    assert conv.agent_id == "agent-1"
    assert conv.user_id == "user-1"
    assert conv.id  # non-empty


@pytest.mark.asyncio
async def test_get_conversation(use_case, user_context):
    conv = await use_case.create_conversation("agent-1", user_context)
    loaded = await use_case.get_conversation(conv.id)
    assert loaded is not None
    assert loaded.id == conv.id


@pytest.mark.asyncio
async def test_get_conversation_not_found(use_case):
    assert await use_case.get_conversation("nonexistent") is None


@pytest.mark.asyncio
async def test_delete_conversation(use_case, user_context):
    conv = await use_case.create_conversation("agent-1", user_context)
    assert await use_case.delete_conversation(conv.id) is True
    assert await use_case.get_conversation(conv.id) is None


@pytest.mark.asyncio
async def test_delete_conversation_not_found(use_case):
    assert await use_case.delete_conversation("nonexistent") is False


@pytest.mark.asyncio
async def test_list_conversations(use_case, user_context):
    await use_case.create_conversation("agent-1", user_context)
    await use_case.create_conversation("agent-2", user_context)
    convs = await use_case.list_conversations("user-1")
    assert len(convs) == 2


@pytest.mark.asyncio
async def test_list_conversations_filters_by_user(use_case):
    ctx_a = UserContext(user_id="alice")
    ctx_b = UserContext(user_id="bob")
    await use_case.create_conversation("a", ctx_a)
    await use_case.create_conversation("b", ctx_b)
    assert len(await use_case.list_conversations("alice")) == 1
    assert len(await use_case.list_conversations("bob")) == 1
