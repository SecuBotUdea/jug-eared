from pydantic import BaseModel


class GamificationResult(BaseModel):
    """Payload que manda Secubot con el resultado de puntos."""
    alert_id: str
    team_id: str
    user_id: str
    points_awarded: bool
    points: int
    message: str

    class Config:
        extra = "forbid"
