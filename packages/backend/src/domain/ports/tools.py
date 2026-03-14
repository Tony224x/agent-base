from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters: dict = field(default_factory=dict)


@dataclass
class ToolResult:
    tool_name: str
    result: str
    is_error: bool = False


class ToolsPort(Protocol):
    async def discover(self) -> list[ToolDefinition]: ...
    async def execute(self, tool_name: str, arguments: dict) -> ToolResult: ...
