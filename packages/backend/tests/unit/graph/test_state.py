from src.graph.state import AgentState


def test_agent_state_has_expected_annotations():
    annotations = AgentState.__annotations__
    assert "messages" in annotations
    assert "pending_ui" in annotations
    assert "tool_calls" in annotations
    assert "user_context" in annotations
    assert "agent_config" in annotations


def test_agent_state_usable_as_dict():
    state = AgentState(
        messages=[],
        pending_ui=None,
        tool_calls=None,
        user_context={"user_id": "u1"},
        agent_config={"name": "test"},
    )
    assert state["messages"] == []
    assert state["pending_ui"] is None
    assert state["user_context"]["user_id"] == "u1"
