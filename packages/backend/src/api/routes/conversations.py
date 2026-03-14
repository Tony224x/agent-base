from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from src.api.dependencies import get_agent_service
from src.domain.services.agent_service import AgentService

router = APIRouter(prefix="/api/conversations")


class CreateConversationRequest(BaseModel):
    agent_id: str = "default-assistant"


class ConversationResponse(BaseModel):
    id: str
    agent_id: str
    created_at: str
    message_count: int


@router.post("", status_code=201)
async def create_conversation(
    body: CreateConversationRequest,
    request: Request,
    service: AgentService = Depends(get_agent_service),
):
    user = request.state.user
    conversation = await service.create_conversation(body.agent_id, user)
    return {
        "id": conversation.id,
        "agent_id": conversation.agent_id,
        "created_at": conversation.created_at.isoformat(),
    }


@router.get("/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    request: Request,
    service: AgentService = Depends(get_agent_service),
):
    conversation = await service.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {
        "id": conversation.id,
        "agent_id": conversation.agent_id,
        "created_at": conversation.created_at.isoformat(),
        "message_count": len(conversation.messages),
        "messages": [
            {
                "id": m.id,
                "role": m.role.value,
                "content": m.content,
                "timestamp": m.timestamp.isoformat(),
            }
            for m in conversation.messages
        ],
    }


@router.delete("/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: str,
    request: Request,
    service: AgentService = Depends(get_agent_service),
):
    deleted = await service.delete_conversation(conversation_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")
