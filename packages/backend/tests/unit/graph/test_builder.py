from unittest.mock import AsyncMock, MagicMock
from pathlib import Path

from src.graph.builder import build_graph
from src.domain.services.contract_validator import ContractValidator

CONTRACTS_DIR = Path(__file__).resolve().parents[4] / "contracts"


def test_build_graph_compiles():
    mock_llm = MagicMock()
    mock_tools = AsyncMock()
    validator = ContractValidator(schemas_dir=CONTRACTS_DIR)

    compiled = build_graph(mock_llm, mock_tools, validator)

    assert compiled is not None
    # Verify the graph has the expected nodes
    node_names = set(compiled.get_graph().nodes.keys())
    assert "chat_node" in node_names
    assert "tool_node" in node_names
    assert "ui_push_node" in node_names
