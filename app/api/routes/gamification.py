import logging
import httpx
from fastapi import APIRouter, BackgroundTasks, status
from app.models.gamification import GamificationResult
from app.config import settings

router = APIRouter(prefix="/gamification", tags=["gamification"])
logger = logging.getLogger("jug-eared.gamification")


async def _notify_discord(payload: GamificationResult) -> None:
    discord_payload = {
        "team_id": payload.team_id,
        "message_content": payload.message,
        "embed_data": {
            "alert_id": payload.alert_id,
            "points": payload.points,
            "points_awarded": payload.points_awarded,
        },
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(settings.discord_url, json=discord_payload)
            response.raise_for_status()
        logger.info(
            "Discord notified | alert_id=%s points_awarded=%s",
            payload.alert_id, payload.points_awarded,
        )
    except Exception:
        logger.exception(
            "Failed to notify Discord | alert_id=%s team=%s",
            payload.alert_id, payload.team_id,
        )


@router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def receive_gamification_result(
    payload: GamificationResult,
    background_tasks: BackgroundTasks,
):
    logger.info(
        "Gamification result received | alert_id=%s team=%s points_awarded=%s points=%s",
        payload.alert_id, payload.team_id, payload.points_awarded, payload.points,
    )
    background_tasks.add_task(_notify_discord, payload)
    return {"status": "received", "alert_id": payload.alert_id}
