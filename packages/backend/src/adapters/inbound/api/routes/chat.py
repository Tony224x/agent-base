from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, Request
from sse_starlette.sse import EventSourceResponse

from src.adapters.inbound.api.dependencies import (
    get_agent_config_dict,
    get_ask_question_use_case,
    get_manage_conversations_use_case,
)
from src.adapters.inbound.api.schemas.chat import SendMessageRequest
from src.core.ports.inbound.ask_question_port import AskQuestionPort
from src.core.ports.inbound.manage_conversations_port import ManageConversationsPort

router = APIRouter(prefix="/api/conversations")


@router.post("/{conversation_id}/messages", status_code=201)
async def send_message(
    conversation_id: str,
    body: SendMessageRequest,
    request: Request,
    conversations: ManageConversationsPort = Depends(get_manage_conversations_use_case),
):
    conversation = await conversations.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {"status": "accepted", "conversation_id": conversation_id}


@router.get("/{conversation_id}/stream")
async def stream_events(
    conversation_id: str,
    request: Request,
    ask: AskQuestionPort = Depends(get_ask_question_use_case),
    conversations: ManageConversationsPort = Depends(get_manage_conversations_use_case),
):
    """SSE endpoint for streaming agent events."""
    conversation = await conversations.get_conversation(conversation_id)
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

        async for event in await ask.execute(
            conversation_id, user_input, user_context, agent_config
        ):
            yield {"data": json.dumps(event)}

    return EventSourceResponse(event_generator())
