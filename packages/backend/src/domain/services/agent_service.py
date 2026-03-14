from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import AsyncIterator, Any

from langchain_core.messages import HumanMessage

from src.domain.models.conversation import Conversation, Message, Role
from src.domain.ports.auth import UserContext


class AgentService:
    """Orchestrates agent conversations: manages state and runs the LangGraph graph."""

    def __init__(self, persistence, graph, validator) -> None:
        self._persistence = persistence
        self._graph = graph
        self._validator = validator

    async def create_conversation(self, agent_id: str, user_context: UserContext) -> Conversation:
        conversation = Conversation(
            agent_id=agent_id,
            user_id=user_context.user_id,
        )
        await self._persistence.save_conversation(conversation)
        return conversation

    async def get_conversation(self, conversation_id: str) -> Conversation | None:
        return await self._persistence.load_conversation(conversation_id)

    async def delete_conversation(self, conversation_id: str) -> bool:
        return await self._persistence.delete_conversation(conversation_id)

    async def list_conversations(self, user_id: str) -> list[Conversation]:
        return await self._persistence.list_conversations(user_id)

    async def handle_message(
        self,
        conversation_id: str,
        user_input: dict,
        user_context: UserContext,
        agent_config_dict: dict,
    ) -> AsyncIterator[dict]:
        """Process a user message and yield SSE events."""
        conversation = await self._persistence.load_conversation(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation not found: {conversation_id}")

        # Build the user message from input
        user_message = self._build_user_message(user_input)
        conversation.add_message(user_message)

        # Build graph input state
        from langchain_core.messages import HumanMessage as LCHumanMessage

        state = {
            "messages": [LCHumanMessage(content=user_message.content)],
            "pending_ui": None,
            "tool_calls": None,
            "user_context": {
                "user_id": user_context.user_id,
                "tenant_id": user_context.tenant_id,
            },
            "agent_config": agent_config_dict,
        }

        # Load previous graph state if exists
        prev_state = await self._persistence.load_graph_state(conversation_id)
        if prev_state and "messages" in prev_state:
            state["messages"] = prev_state["messages"] + state["messages"]

        # Run the graph and yield events
        now = datetime.now(timezone.utc).isoformat()

        async for event in self._graph.astream(state, stream_mode="updates"):
            for node_name, node_output in event.items():
                # Yield token events for chat node responses
                if node_name == "chat_node" and "messages" in node_output:
                    for msg in node_output["messages"]:
                        if hasattr(msg, "content") and msg.content:
                            conversation.add_message(
                                Message(role=Role.ASSISTANT, content=msg.content)
                            )
                            yield {
                                "eventType": "token",
                                "conversationId": conversation_id,
                                "timestamp": now,
                                "token": msg.content,
                            }

                # Yield component events for UI push
                if node_name == "ui_push_node" and "pending_ui" in node_output:
                    for component in (node_output["pending_ui"] or []):
                        yield {
                            "eventType": "component",
                            "conversationId": conversation_id,
                            "timestamp": now,
                            "component": component,
                        }

                # Yield tool events
                if node_name == "tool_node" and "messages" in node_output:
                    for msg in node_output["messages"]:
                        if hasattr(msg, "name"):
                            yield {
                                "eventType": "tool_end",
                                "conversationId": conversation_id,
                                "timestamp": now,
                                "toolName": msg.name,
                            }

        # Save updated conversation and graph state
        await self._persistence.save_conversation(conversation)

        # Yield done event
        yield {
            "eventType": "done",
            "conversationId": conversation_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _build_user_message(self, user_input: dict) -> Message:
        input_type = user_input.get("type", "text")

        if input_type == "text":
            content = user_input.get("text", "")
        elif input_type == "form_submit":
            form_data = user_input.get("formData", {})
            content = f"[Form submitted] {form_data}"
        elif input_type == "choice_select":
            choices = user_input.get("selectedChoices", [])
            content = f"[Selected] {', '.join(choices)}"
        elif input_type == "confirmation":
            confirmed = user_input.get("confirmed", False)
            content = "[Confirmed]" if confirmed else "[Cancelled]"
        elif input_type == "card_action":
            action_id = user_input.get("cardActionId", "")
            card_id = user_input.get("cardId", "")
            content = f"[Card action: {action_id} on card {card_id}]"
        else:
            content = str(user_input)

        return Message(role=Role.USER, content=content)
