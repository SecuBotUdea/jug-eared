import logging
from fastapi import APIRouter, BackgroundTasks, Header, status
from app.models.alert import IncomingAlert
from app.core.router import route_alert_to_secubot
from app.db.repository import repo

router = APIRouter(prefix="/alerts", tags=["alerts"])
logger = logging.getLogger("jug-eared.alerts")


@router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def receive_alert(
    alert: IncomingAlert,
    background_tasks: BackgroundTasks,
    x_source: str = Header(default="unknown"),
):
    logger.info("Alert received | alert_id=%s source=%s", alert.alert_id, x_source)
    background_tasks.add_task(route_alert_to_secubot, alert, repo)
    return {"status": "received", "alert_id": alert.alert_id}