from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from src.adapters.inbound.api.dependencies import get_extract_client_info_use_case
from src.core.ports.inbound.extract_client_info_port import ExtractClientInfoPort

router = APIRouter(prefix="/api/conversations")


@router.get("/{conversation_id}/extract")
async def extract_client_info(
    conversation_id: str,
    use_case: ExtractClientInfoPort = Depends(get_extract_client_info_use_case),
):
    """Extract structured client information from a conversation."""
    try:
        result = await use_case.execute(conversation_id)
    except NotImplementedError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc
    return result
