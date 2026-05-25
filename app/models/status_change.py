from pydantic import BaseModel


class StatusChangePayload(BaseModel):
    """Payload que manda el parser cuando una alerta cambia de status."""
    alert_id: str
    source_type: str
    previous_status: str
    current_status: str
    component: str
    severity: str

    class Config:
        extra = "forbid"
