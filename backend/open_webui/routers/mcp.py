import logging
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Any, Optional

from open_webui.utils.mcp.client import MCPClient
from open_webui.utils.auth import get_verified_user

router = APIRouter()
log = logging.getLogger(__name__)

class ElicitationResponseForm(BaseModel):
    action: str
    data: Optional[Any] = None

@router.post("/elicitation/{request_id}")
async def resolve_elicitation(
    request_id: str,
    form_data: ElicitationResponseForm,
    user=Depends(get_verified_user)
):
    try:
        payload = form_data.model_dump()
        if payload.get("data") is not None:
            payload["content"] = payload.pop("data")
        MCPClient.resolve_elicitation(request_id, payload)
        return {"status": True}
    except Exception as e:
        log.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resolve elicitation",
        )
