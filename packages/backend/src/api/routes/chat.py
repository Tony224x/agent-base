from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from src.api.dependencies import get_agent_service, get_agent_config_dict
from src.domain.services.agent_service import AgentService

router = APIRouter(prefix="/api/conversations")


class SendMessageRequest(BaseModel):
    type: str = "text"
    text: str | None = None
    formData: dict | None = None
    selectedChoices: list[str] | None = None
    confirmed: bool | None = None
    cardActionId: str | None = None
    cardId: str | None = None


@router.post("/{conversation_id}/messages", status_code=201)
async def send_message(
    conversation_id: str,
    body: SendMessageRequest,
    request: Request,
    service: AgentService = Depends(get_agent_service),
):
    conversation = await service.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {"status": "accepted", "conversation_id": conversation_id}


@router.get("/{conversation_id}/stream")
async def stream_events(
    conversation_id: str,
    request: Request,
    service: AgentService = Depends(get_agent_service),
):
    """SSE endpoint for streaming agent events."""
    conversation = await service.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    async def event_generator():
        user_context = request.state.user
        agent_config = get_agent_config_dict()

        # Get the last user message as input
        last_message = conversation.messages[-1] if conversation.messages else None
        if not last_message:
            yield {"data": json.dumps({"eventType": "done", "conversationId": conversation_id})}
            return

        user_input = {"type": "text", "text": last_message.content}

        async for event in service.handle_message(
            conversation_id, user_input, user_context, agent_config
        ):
            yield {"data": json.dumps(event)}

    return EventSourceResponse(event_generator())
