from app.models.alert import AlertSource, AlertSeverity, AlertStatus
from pydantic import BaseModel
from typing import Optional


class DiscordNotification(BaseModel):
    alert_id: str
    title: str
    severity: AlertSeverity
    status: AlertStatus
    component: str
    location: Optional[str] = None
    source_type: AlertSource
    team_id: str
    team_name: str

    class Config:
        extra = "forbid"