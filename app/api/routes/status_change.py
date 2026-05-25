import logging
import httpx
from fastapi import APIRouter, BackgroundTasks, status
from app.models.status_change import StatusChangePayload
from app.config import settings

router = APIRouter(prefix="/alerts", tags=["status-change"])
logger = logging.getLogger("jug-eared.status_change")


async def _forward_to_secubot(payload: StatusChangePayload) -> None:
    secubot_payload = {
        "alert_id": payload.alert_id,
        "previous_status": payload.previous_status,
        "current_status": payload.current_status,
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        await client.post(
            f"{settings.secubot_url}/status-change",
            json=secubot_payload,
        )
    logger.info(
        "Status change forwarded to secubot | alert_id=%s %s→%s",
        payload.alert_id, payload.previous_status, payload.current_status,
    )


@router.post("/status-change", status_code=status.HTTP_202_ACCEPTED)
async def receive_status_change(
    payload: StatusChangePayload,
    background_tasks: BackgroundTasks,
):
    """
    Recibe cambios de status del parser.
    Forwardea a Secubot para que calcule gamificación.
    """
    logger.info(
        "Status change received | alert_id=%s %s→%s",
        payload.alert_id, payload.previous_status, payload.current_status,
    )
    background_tasks.add_task(_forward_to_secubot, payload)
    return {"status": "received", "alert_id": payload.alert_id}
