from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request

from src.adapters.inbound.api.dependencies import get_manage_conversations_use_case
from src.adapters.inbound.api.schemas.chat import CreateConversationRequest
from src.core.ports.inbound.manage_conversations_port import ManageConversationsPort

router = APIRouter(prefix="/api/conversations")


@router.post("", status_code=201)
async def create_conversation(
    body: CreateConversationRequest,
    request: Request,
    use_case: ManageConversationsPort = Depends(get_manage_conversations_use_case),
):
    user = request.state.user
    conversation = await use_case.create_conversation(body.agent_id, user)
    return {
        "id": conversation.id,
        "agent_id": conversation.agent_id,
        "created_at": conversation.created_at.isoformat(),
    }


@router.get("/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    request: Request,
    use_case: ManageConversationsPort = Depends(get_manage_conversations_use_case),
):
    conversation = await use_case.get_conversation(conversation_id)
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
    use_case: ManageConversationsPort = Depends(get_manage_conversations_use_case),
):
    deleted = await use_case.delete_conversation(conversation_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")
