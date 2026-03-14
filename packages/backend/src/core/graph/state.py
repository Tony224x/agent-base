from __future__ import annotations

from typing import Annotated

from langgraph.graph.message import add_messages


class AgentState(dict):
    """LangGraph agent state.

    Fields:
        messages: Conversation history (managed by LangGraph's add_messages reducer)
        pending_ui: UI components to push to the client
        tool_calls: Pending tool calls
        user_context: User info extracted from auth token
        agent_config: Active agent configuration
    """

    __annotations__ = {
        "messages": Annotated[list, add_messages],
        "pending_ui": list[dict] | None,
        "tool_calls": list[dict] | None,
        "user_context": dict,
        "agent_config": dict,
    }
