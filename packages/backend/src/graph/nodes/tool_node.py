from __future__ import annotations

from langchain_core.messages import ToolMessage

from src.domain.ports.tools import ToolsPort


def make_tool_node(tools_port: ToolsPort):
    """Create a tool execution node that runs tools via the ToolsPort."""

    async def tool_node(state: dict) -> dict:
        last_message = state["messages"][-1]
        results = []

        for tool_call in last_message.tool_calls:
            if tool_call["name"] == "push_ui":
                continue  # Handled by ui_push_node

            result = await tools_port.execute(tool_call["name"], tool_call["args"])
            results.append(
                ToolMessage(
                    content=result.result,
                    tool_call_id=tool_call["id"],
                    name=tool_call["name"],
                )
            )

        return {"messages": results}

    return tool_node
