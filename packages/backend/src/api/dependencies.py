from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from src.adapters.auth.jwt_adapter import JWTAuthAdapter
from src.adapters.llm.langchain_adapter import create_llm
from src.adapters.persistence.memory_adapter import InMemoryPersistenceAdapter
from src.adapters.tools.mcp_adapter import MCPToolsAdapter
from src.domain.services.agent_service import AgentService
from src.domain.services.config_loader import load_agent_config
from src.domain.services.contract_validator import ContractValidator
from src.graph.builder import build_graph


def _get_contracts_dir() -> Path:
    """Resolve the contracts directory."""
    # When running from packages/backend/, contracts is a sibling package
    backend_dir = Path(__file__).resolve().parents[2]
    contracts_dir = backend_dir.parent / "contracts"
    if contracts_dir.exists():
        return contracts_dir
    # Fallback: mounted in Docker at /app/contracts
    docker_contracts = Path("/app/contracts")
    if docker_contracts.exists():
        return docker_contracts
    raise FileNotFoundError("Cannot find contracts directory")


@lru_cache
def get_auth_adapter() -> JWTAuthAdapter:
    return JWTAuthAdapter(
        secret=os.environ.get("JWT_SECRET", "dev-secret-change-me"),
        algorithm=os.environ.get("JWT_ALGORITHM", "HS256"),
    )


@lru_cache
def get_persistence_adapter() -> InMemoryPersistenceAdapter:
    return InMemoryPersistenceAdapter()


@lru_cache
def get_contract_validator() -> ContractValidator:
    return ContractValidator(schemas_dir=_get_contracts_dir())


@lru_cache
def get_mcp_adapter() -> MCPToolsAdapter:
    config_path = os.environ.get("MCP_CONFIG_PATH", "config/mcp_servers.yaml")
    return MCPToolsAdapter(config_path=config_path)


def get_agent_config_dict() -> dict:
    config_path = os.environ.get("DEFAULT_AGENT_CONFIG", "config/agents/default.yaml")
    config = load_agent_config(config_path)
    return {
        "name": config.name,
        "model": config.model,
        "system_prompt": config.system_prompt,
        "allowed_tools": config.allowed_tools,
        "allowed_ui_components": config.allowed_ui_components,
        "max_turns": config.max_turns,
        "temperature": config.temperature,
    }


def get_compiled_graph():
    config_path = os.environ.get("DEFAULT_AGENT_CONFIG", "config/agents/default.yaml")
    config = load_agent_config(config_path)
    llm = create_llm(
        provider=os.environ.get("LLM_PROVIDER", "openai"),
        model=config.model,
        temperature=config.temperature,
    )
    tools_port = get_mcp_adapter()
    validator = get_contract_validator()

    # Bind push_ui as a tool the LLM can call
    push_ui_tool = {
        "type": "function",
        "function": {
            "name": "push_ui",
            "description": "Push a UI component to the user. The payload must match a valid component schema (form, choice-list, confirmation, card-list, or message).",
            "parameters": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": config.allowed_ui_components,
                        "description": "The component type",
                    },
                },
                "required": ["type"],
                "additionalProperties": True,
            },
        },
    }
    llm_with_tools = llm.bind_tools([push_ui_tool])

    return build_graph(llm_with_tools, tools_port, validator)


def get_agent_service() -> AgentService:
    return AgentService(
        persistence=get_persistence_adapter(),
        graph=get_compiled_graph(),
        validator=get_contract_validator(),
    )
