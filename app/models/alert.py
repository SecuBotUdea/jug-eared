from enum import Enum
from typing import Optional
from pydantic import BaseModel


class AlertSource(str, Enum):
    dependabot = "dependabot"
    zap = "zap"
    trivy = "trivy"


class AlertSeverity(str, Enum):
    informational = "informational"
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"
    unknown = "unknown"


class AlertStatus(str, Enum):
    open = "open"
    fixed = "fixed"
    dismissed = "dismissed"
    resolved = "resolved"
    unknown = "unknown"


class IncomingAlert(BaseModel):
    """
    Payload exacto que el parser envía a jug-eared.
    """
    alert_id: str
    source_type: AlertSource
    source_id: str
    title: str
    severity: AlertSeverity = AlertSeverity.unknown
    status: AlertStatus = AlertStatus.unknown
    component: str
    location: Optional[str] = None
    external_references_score: Optional[float] = None
    normalized_payload: dict = {}

    class Config:
        extra = "forbid"