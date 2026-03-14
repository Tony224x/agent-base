from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AgentConfig:
    name: str
    model: str
    system_prompt: str
    allowed_tools: list[str] = field(default_factory=lambda: ["*"])
    allowed_ui_components: list[str] = field(default_factory=list)
    max_turns: int = 20
    temperature: float = 0.7

    def allows_tool(self, tool_name: str) -> bool:
        return "*" in self.allowed_tools or tool_name in self.allowed_tools

    def allows_ui_component(self, component_type: str) -> bool:
        return component_type in self.allowed_ui_components
