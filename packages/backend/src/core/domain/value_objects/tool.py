from __future__ import annotations

from dataclasses import dataclass, field


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
