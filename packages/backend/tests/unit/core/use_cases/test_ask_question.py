from __future__ import annotations

import pytest

from src.core.domain.value_objects.user_context import UserContext
from src.core.use_cases.ask_question import AskQuestionUseCase


class FakeAgentService:
    """Fake AgentService that yields canned events."""

    def __init__(self, events: list[dict] | None = None) -> None:
        self._events = events or [
            {"eventType": "token", "token": "hello"},
            {"eventType": "done"},
        ]

    async def handle_message(
        self,
        conversation_id: str,
        user_input: dict,
        user_context: UserContext,
        agent_config_dict: dict,
    ):
        for event in self._events:
            yield event


@pytest.fixture
def user_context():
    return UserContext(user_id="user-1", tenant_id="tenant-1")


@pytest.mark.asyncio
async def test_execute_delegates_to_agent_service(user_context):
    fake_service = FakeAgentService()
    use_case = AskQuestionUseCase(agent_service=fake_service)

    result = await use_case.execute(
        conversation_id="conv-1",
        user_input={"type": "text", "text": "hi"},
        user_context=user_context,
        agent_config={"model": "gpt-4"},
    )

    events = [event async for event in result]
    assert len(events) == 2
    assert events[0]["eventType"] == "token"
    assert events[1]["eventType"] == "done"


@pytest.mark.asyncio
async def test_execute_passes_arguments_correctly(user_context):
    """Verify the use case forwards all arguments to the service."""
    captured = {}

    class CapturingService:
        async def handle_message(self, *, conversation_id, user_input, user_context, agent_config_dict):
            captured["conversation_id"] = conversation_id
            captured["user_input"] = user_input
            captured["user_context"] = user_context
            captured["agent_config_dict"] = agent_config_dict
            return
            yield  # make it an async generator  # noqa: RUF027

    use_case = AskQuestionUseCase(agent_service=CapturingService())
    result = await use_case.execute(
        conversation_id="c-99",
        user_input={"type": "text", "text": "hello"},
        user_context=user_context,
        agent_config={"model": "gpt-4"},
    )
    # Consume the iterator
    _ = [event async for event in result]

    assert captured["conversation_id"] == "c-99"
    assert captured["user_input"] == {"type": "text", "text": "hello"}
    assert captured["user_context"] is user_context
    assert captured["agent_config_dict"] == {"model": "gpt-4"}
