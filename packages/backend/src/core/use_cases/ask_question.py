from __future__ import annotations

from typing import AsyncIterator

from src.core.domain.services.agent_service import AgentService
from src.core.domain.value_objects.user_context import UserContext


class AskQuestionUseCase:
    """Use case: Ask a question to the agent and get a streamed response.

    Thin wrapper around AgentService.handle_message — provides a seam
    for future cross-cutting concerns (logging, rate-limiting, etc.).
    """

    def __init__(self, agent_service: AgentService) -> None:
        self._agent_service = agent_service

    async def execute(
        self,
        conversation_id: str,
        user_input: dict,
        user_context: UserContext,
        agent_config: dict,
    ) -> AsyncIterator[dict]:
        return self._agent_service.handle_message(
            conversation_id=conversation_id,
            user_input=user_input,
            user_context=user_context,
            agent_config_dict=agent_config,
        )
