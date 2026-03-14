from __future__ import annotations

import logging
from pathlib import Path

import yaml
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from src.domain.ports.tools import ToolDefinition, ToolResult

logger = logging.getLogger(__name__)


class MCPToolsAdapter:
    """Connects to MCP servers defined in config, discovers and executes tools."""

    def __init__(self, config_path: str | Path) -> None:
        self._config_path = Path(config_path)
        self._sessions: dict[str, ClientSession] = {}
        self._tool_map: dict[str, str] = {}  # tool_name -> server_name
        self._contexts: list = []

    async def initialize(self) -> None:
        """Connect to all MCP servers defined in config."""
        if not self._config_path.exists():
            logger.warning("MCP config not found at %s, no tools available", self._config_path)
            return

        config = yaml.safe_load(self._config_path.read_text(encoding="utf-8"))
        servers = config.get("servers", [])

        for server_config in servers:
            name = server_config["name"]
            try:
                server_params = StdioServerParameters(
                    command=server_config["command"],
                    args=server_config.get("args", []),
                    env=server_config.get("env"),
                )
                ctx = stdio_client(server_params)
                read, write = await ctx.__aenter__()
                self._contexts.append(ctx)

                session = ClientSession(read, write)
                await session.__aenter__()

                await session.initialize()
                self._sessions[name] = session
                logger.info("Connected to MCP server: %s", name)
            except Exception:
                logger.exception("Failed to connect to MCP server: %s", name)

    async def discover(self) -> list[ToolDefinition]:
        """Discover tools from all connected MCP servers."""
        tools = []
        for name, session in self._sessions.items():
            try:
                server_tools = await session.list_tools()
                for tool in server_tools.tools:
                    tools.append(
                        ToolDefinition(
                            name=tool.name,
                            description=tool.description or "",
                            parameters=tool.inputSchema or {},
                        )
                    )
                    self._tool_map[tool.name] = name
            except Exception:
                logger.exception("Failed to discover tools from: %s", name)
        return tools

    async def execute(self, tool_name: str, arguments: dict) -> ToolResult:
        """Execute a tool by name."""
        server_name = self._tool_map.get(tool_name)
        if not server_name:
            return ToolResult(
                tool_name=tool_name,
                result=f"Unknown tool: {tool_name}",
                is_error=True,
            )

        session = self._sessions[server_name]
        try:
            result = await session.call_tool(tool_name, arguments=arguments)
            content = "\n".join(
                block.text if hasattr(block, "text") else str(block)
                for block in result.content
            )
            return ToolResult(tool_name=tool_name, result=content)
        except Exception as e:
            logger.exception("Tool execution failed: %s", tool_name)
            return ToolResult(tool_name=tool_name, result=str(e), is_error=True)

    async def shutdown(self) -> None:
        """Close all MCP sessions and connections."""
        for session in self._sessions.values():
            try:
                await session.__aexit__(None, None, None)
            except Exception:
                pass
        for ctx in self._contexts:
            try:
                await ctx.__aexit__(None, None, None)
            except Exception:
                pass
        self._sessions.clear()
        self._contexts.clear()
        self._tool_map.clear()
