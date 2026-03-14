from __future__ import annotations

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage


def make_chat_node(llm: BaseChatModel):
    """Create a chat node that invokes the LLM with conversation history."""

    async def chat_node(state: dict) -> dict:
        config = state["agent_config"]
        system = SystemMessage(content=config["system_prompt"])
        messages = [system] + state["messages"]
        response = await llm.ainvoke(messages)
        return {"messages": [response]}

    return chat_node
