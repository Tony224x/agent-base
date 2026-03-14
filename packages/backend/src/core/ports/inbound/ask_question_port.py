from __future__ import annotations

from typing import AsyncIterator, Protocol

from src.core.domain.value_objects.user_context import UserContext


class AskQuestionPort(Protocol):
    """Inbound port for asking a question and streaming the agent response."""

    async def execute(
        self,
        conversation_id: str,
        user_input: dict,
        user_context: UserContext,
        agent_config: dict,
    ) -> AsyncIterator[dict]: ...
