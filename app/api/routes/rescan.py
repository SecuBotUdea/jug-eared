import logging
from fastapi import APIRouter, BackgroundTasks, status
from app.models.rescan import RescanRequest
from app.core.router import route_rescan
from app.db.repository import repo

router = APIRouter(prefix="/rescan", tags=["rescan"])
logger = logging.getLogger("jug-eared.rescan")


@router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def receive_rescan(
    payload: RescanRequest,
    background_tasks: BackgroundTasks,
):
    logger.info(
        "Rescan request accepted | alert_id=%s user_id=%r guild_id=%s action=%s",
        payload.alert_id,
        payload.user_id,
        payload.guild_id,
        payload.action,
    )
    background_tasks.add_task(route_rescan, payload, repo)
    return {"status": "received", "alert_id": payload.alert_id}