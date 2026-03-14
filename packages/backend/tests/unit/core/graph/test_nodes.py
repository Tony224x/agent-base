import pytest
from unittest.mock import AsyncMock
from pathlib import Path

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from src.core.graph.nodes.chat_node import make_chat_node
from src.core.graph.nodes.tool_node import make_tool_node
from src.core.graph.nodes.ui_push_node import make_ui_push_node
from src.core.domain.value_objects.tool import ToolResult
from src.core.domain.services.contract_validator import ContractValidator

CONTRACTS_DIR = Path(__file__).resolve().parents[5] / "contracts"


def _base_state(**overrides):
    state = {
        "messages": [],
        "agent_config": {
            "system_prompt": "You are helpful.",
            "model": "gpt-4o",
        },
        "user_context": {"user_id": "u1"},
        "pending_ui": None,
        "tool_calls": None,
    }
    state.update(overrides)
    return state


@pytest.mark.asyncio
async def test_chat_node_returns_ai_message():
    mock_llm = AsyncMock()
    mock_llm.ainvoke.return_value = AIMessage(content="Hello!")

    chat = make_chat_node(mock_llm)
    state = _base_state(messages=[HumanMessage(content="Hi")])

    result = await chat(state)

    assert "messages" in result
    assert len(result["messages"]) == 1
    assert result["messages"][0].content == "Hello!"
    mock_llm.ainvoke.assert_called_once()


@pytest.mark.asyncio
async def test_chat_node_prepends_system_message():
    mock_llm = AsyncMock()
    mock_llm.ainvoke.return_value = AIMessage(content="ok")

    chat = make_chat_node(mock_llm)
    state = _base_state(messages=[HumanMessage(content="Hi")])

    await chat(state)

    call_args = mock_llm.ainvoke.call_args[0][0]
    assert call_args[0].content == "You are helpful."  # SystemMessage
    assert call_args[1].content == "Hi"  # HumanMessage


@pytest.mark.asyncio
async def test_tool_node_executes_tools():
    mock_tools = AsyncMock()
    mock_tools.execute.return_value = ToolResult(
        tool_name="search", result="Found 3 results"
    )

    ai_msg = AIMessage(
        content="",
        tool_calls=[{"name": "search", "args": {"q": "test"}, "id": "tc1"}],
    )
    state = _base_state(messages=[ai_msg])

    node = make_tool_node(mock_tools)
    result = await node(state)

    assert len(result["messages"]) == 1
    assert isinstance(result["messages"][0], ToolMessage)
    assert result["messages"][0].content == "Found 3 results"
    assert result["messages"][0].tool_call_id == "tc1"


@pytest.mark.asyncio
async def test_tool_node_skips_push_ui():
    mock_tools = AsyncMock()

    ai_msg = AIMessage(
        content="",
        tool_calls=[
            {"name": "push_ui", "args": {"type": "form"}, "id": "tc1"},
            {"name": "search", "args": {"q": "test"}, "id": "tc2"},
        ],
    )
    state = _base_state(messages=[ai_msg])

    mock_tools.execute.return_value = ToolResult(tool_name="search", result="ok")

    node = make_tool_node(mock_tools)
    result = await node(state)

    assert len(result["messages"]) == 1
    assert result["messages"][0].name == "search"


@pytest.mark.asyncio
async def test_ui_push_node_validates_and_queues():
    validator = ContractValidator(schemas_dir=CONTRACTS_DIR)

    ai_msg = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "push_ui",
                "args": {
                    "type": "form",
                    "title": "Test",
                    "fields": [
                        {"name": "email", "fieldType": "email", "label": "Email"}
                    ],
                },
                "id": "tc1",
            }
        ],
    )
    state = _base_state(messages=[ai_msg])

    node = make_ui_push_node(validator)
    result = await node(state)

    assert len(result["pending_ui"]) == 1
    assert result["pending_ui"][0]["type"] == "form"
    assert len(result["messages"]) == 1
    assert "pushed to user" in result["messages"][0].content


@pytest.mark.asyncio
async def test_ui_push_node_rejects_invalid():
    validator = ContractValidator(schemas_dir=CONTRACTS_DIR)

    ai_msg = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "push_ui",
                "args": {"type": "form"},  # missing required fields
                "id": "tc1",
            }
        ],
    )
    state = _base_state(messages=[ai_msg])

    node = make_ui_push_node(validator)

    with pytest.raises(ValueError, match="Invalid form component"):
        await node(state)
