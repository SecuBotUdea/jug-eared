from typing import Any
from pydantic import BaseModel, Field


class RescanRequest(BaseModel):
    """Payload que llega de Discord — espeja ActionWebhookPayload."""
    action: str
    alert_id: str
    guild_id: str
    user_id: str

    class Config:
        extra = "forbid"