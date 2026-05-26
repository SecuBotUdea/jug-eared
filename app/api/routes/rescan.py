import logging
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status
from pydantic import ValidationError
from app.models.rescan import RescanRequest
from app.core.router import route_rescan

router = APIRouter(prefix="/rescan", tags=["rescan"])
logger = logging.getLogger("jug-eared.rescan")


@router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def receive_rescan(
    request: Request,
    background_tasks: BackgroundTasks,
):
    raw_body = await request.json()
    logger.info("Rescan raw body received | body=%s", raw_body)

    try:
        payload = RescanRequest(**raw_body)
    except ValidationError as exc:
        logger.error(
            "Rescan payload validation failed | body=%s errors=%s",
            raw_body,
            exc.errors(),
        )
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.errors())

    logger.info(
        "Rescan request parsed | alert_id=%s user_id=%s guild_id=%s",
        payload.alert_id,
        payload.user_id,
        payload.guild_id,
    )
    background_tasks.add_task(route_rescan, payload)
    return {"status": "received", "alert_id": payload.alert_id}
