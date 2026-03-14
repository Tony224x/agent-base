from __future__ import annotations

from langchain_core.messages import ToolMessage

from src.domain.services.contract_validator import ContractValidator


def make_ui_push_node(validator: ContractValidator):
    """Create a UI push node that validates and queues UI components."""

    async def ui_push_node(state: dict) -> dict:
        last_message = state["messages"][-1]
        pending_ui = []
        tool_messages = []

        for tool_call in last_message.tool_calls:
            if tool_call["name"] != "push_ui":
                continue

            payload = tool_call["args"]
            validator.validate_component(payload)
            pending_ui.append(payload)

            tool_messages.append(
                ToolMessage(
                    content=f"UI component '{payload['type']}' pushed to user.",
                    tool_call_id=tool_call["id"],
                    name="push_ui",
                )
            )

        return {"messages": tool_messages, "pending_ui": pending_ui}

    return ui_push_node
