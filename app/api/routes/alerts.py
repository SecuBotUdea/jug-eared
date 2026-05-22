import logging
from fastapi import APIRouter, Header, status
from app.models.alert import IncomingAlert

router = APIRouter(prefix="/alerts", tags=["alerts"])
logger = logging.getLogger("jug-eared.alerts")


@router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def receive_alert(
    alert: IncomingAlert,
    x_source: str = Header(default="unknown"),
):
    """
    Recibe alertas normalizadas del parser.
    Por ahora solo las registra. El routing a Secubot y Discord viene después.
    """
    logger.info(
        "Alert received | alert_id=%s source=%s severity=%s status=%s",
        alert.alert_id,
        x_source,
        alert.severity,
        alert.status,
    )
    return {"status": "received", "alert_id": alert.alert_id}