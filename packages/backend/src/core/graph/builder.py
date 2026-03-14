from __future__ import annotations

from langchain_core.language_models import BaseChatModel
from langgraph.graph import StateGraph, END

from src.core.graph.state import AgentState
from src.core.graph.nodes.chat_node import make_chat_node
from src.core.graph.nodes.tool_node import make_tool_node
from src.core.graph.nodes.ui_push_node import make_ui_push_node
from src.core.graph.edges import route_after_llm
from src.core.ports.outbound.tools_port import ToolsPort
from src.core.domain.services.contract_validator import ContractValidator


def build_graph(
    llm: BaseChatModel,
    tools_port: ToolsPort,
    validator: ContractValidator,
):
    """Build and compile the agent graph.

    Graph structure:
        START -> chat_node -> [tool_node | ui_push_node | END]
                              |              |
                          chat_node      chat_node
    """
    graph = StateGraph(AgentState)

    graph.add_node("chat_node", make_chat_node(llm))
    graph.add_node("tool_node", make_tool_node(tools_port))
    graph.add_node("ui_push_node", make_ui_push_node(validator))

    graph.set_entry_point("chat_node")

    graph.add_conditional_edges(
        "chat_node",
        route_after_llm,
        {
            "tool_node": "tool_node",
            "ui_push_node": "ui_push_node",
            END: END,
        },
    )
    graph.add_edge("tool_node", "chat_node")
    graph.add_edge("ui_push_node", "chat_node")

    return graph.compile()
