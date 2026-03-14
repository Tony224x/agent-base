from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END

from src.core.graph.edges import route_after_llm


def test_route_to_end_when_no_tool_calls():
    state = {"messages": [AIMessage(content="Done")]}
    assert route_after_llm(state) == END


def test_route_to_end_when_human_message():
    state = {"messages": [HumanMessage(content="Hi")]}
    assert route_after_llm(state) == END


def test_route_to_tool_when_tool_calls():
    msg = AIMessage(
        content="",
        tool_calls=[{"name": "search", "args": {}, "id": "1"}],
    )
    state = {"messages": [msg]}
    assert route_after_llm(state) == "tool_node"


def test_route_to_ui_push_when_push_ui():
    msg = AIMessage(
        content="",
        tool_calls=[{"name": "push_ui", "args": {"type": "form"}, "id": "1"}],
    )
    state = {"messages": [msg]}
    assert route_after_llm(state) == "ui_push_node"


def test_route_to_ui_push_when_mixed_with_push_ui():
    msg = AIMessage(
        content="",
        tool_calls=[
            {"name": "push_ui", "args": {"type": "form"}, "id": "1"},
            {"name": "search", "args": {}, "id": "2"},
        ],
    )
    state = {"messages": [msg]}
    # push_ui takes priority
    assert route_after_llm(state) == "ui_push_node"


def test_route_to_end_with_empty_tool_calls():
    msg = AIMessage(content="Done", tool_calls=[])
    state = {"messages": [msg]}
    assert route_after_llm(state) == END
