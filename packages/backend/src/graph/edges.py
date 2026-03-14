from __future__ import annotations

from langgraph.graph import END


def route_after_llm(state: dict) -> str:
    """Route after LLM response: to tool_node, ui_push_node, or END."""
    last = state["messages"][-1]

    if not hasattr(last, "tool_calls") or not last.tool_calls:
        return END

    has_ui = any(tc["name"] == "push_ui" for tc in last.tool_calls)
    has_tools = any(tc["name"] != "push_ui" for tc in last.tool_calls)

    if has_ui:
        return "ui_push_node"
    if has_tools:
        return "tool_node"

    return END
