import pytest

from src.adapters.persistence.memory_adapter import InMemoryPersistenceAdapter
from src.domain.models.conversation import Conversation, Message, Role


@pytest.fixture
def adapter():
    return InMemoryPersistenceAdapter()


@pytest.mark.asyncio
async def test_save_and_load_conversation(adapter):
    conv = Conversation(agent_id="test", user_id="u1")
    conv.add_message(Message(role=Role.USER, content="hello"))
    await adapter.save_conversation(conv)

    loaded = await adapter.load_conversation(conv.id)
    assert loaded is not None
    assert loaded.id == conv.id
    assert len(loaded.messages) == 1


@pytest.mark.asyncio
async def test_load_nonexistent_returns_none(adapter):
    loaded = await adapter.load_conversation("nonexistent")
    assert loaded is None


@pytest.mark.asyncio
async def test_list_conversations(adapter):
    conv1 = Conversation(agent_id="test", user_id="u1")
    conv2 = Conversation(agent_id="test", user_id="u1")
    conv3 = Conversation(agent_id="test", user_id="u2")
    await adapter.save_conversation(conv1)
    await adapter.save_conversation(conv2)
    await adapter.save_conversation(conv3)

    result = await adapter.list_conversations("u1")
    assert len(result) == 2


@pytest.mark.asyncio
async def test_delete_conversation(adapter):
    conv = Conversation(agent_id="test")
    await adapter.save_conversation(conv)
    await adapter.save_graph_state(conv.id, {"key": "value"})

    assert await adapter.delete_conversation(conv.id) is True
    assert await adapter.load_conversation(conv.id) is None
    assert await adapter.load_graph_state(conv.id) is None


@pytest.mark.asyncio
async def test_delete_nonexistent_returns_false(adapter):
    assert await adapter.delete_conversation("nonexistent") is False


@pytest.mark.asyncio
async def test_save_and_load_graph_state(adapter):
    await adapter.save_graph_state("conv1", {"messages": [], "step": 3})
    state = await adapter.load_graph_state("conv1")
    assert state is not None
    assert state["step"] == 3


@pytest.mark.asyncio
async def test_load_nonexistent_graph_state(adapter):
    state = await adapter.load_graph_state("nonexistent")
    assert state is None
