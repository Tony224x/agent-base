from __future__ import annotations

from pathlib import Path

import yaml

from src.core.domain.entities.agent_config import AgentConfig


def load_agent_config(config_path: str | Path) -> AgentConfig:
    """Load an agent configuration from a YAML file."""
    data = yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))
    return AgentConfig(**data)
