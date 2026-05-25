import logging
from fastapi import APIRouter, status
from app.models.gamification import GamificationResult

router = APIRouter(prefix="/gamification", tags=["gamification"])
logger = logging.getLogger("jug-eared.gamification")


@router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def receive_gamification_result(payload: GamificationResult):
    """
    Recibe el resultado de gamificación de Secubot.
    Por ahora solo lo registra. Notificación a Discord viene después.
    """
    logger.info(
        "Gamification result received | alert_id=%s team=%s points_awarded=%s points=%s",
        payload.alert_id, payload.team_id, payload.points_awarded, payload.points,
    )
    return {"status": "received", "alert_id": payload.alert_id}
