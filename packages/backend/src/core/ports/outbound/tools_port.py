from __future__ import annotations

from typing import Protocol

from src.core.domain.value_objects.tool import ToolDefinition, ToolResult


class ToolsPort(Protocol):
    async def discover(self) -> list[ToolDefinition]: ...
    async def execute(self, tool_name: str, arguments: dict) -> ToolResult: ...
