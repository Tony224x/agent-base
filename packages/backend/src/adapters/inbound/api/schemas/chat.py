from __future__ import annotations

from pydantic import BaseModel


class SendMessageRequest(BaseModel):
    type: str = "text"
    text: str | None = None
    formData: dict | None = None
    selectedChoices: list[str] | None = None
    confirmed: bool | None = None
    cardActionId: str | None = None
    cardId: str | None = None


class CreateConversationRequest(BaseModel):
    agent_id: str = "default-assistant"


class ConversationResponse(BaseModel):
    id: str
    agent_id: str
    created_at: str
    message_count: int
