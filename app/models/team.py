from pydantic import BaseModel


class Team(BaseModel):
    team_id: str
    name: str
    repository: str  # ej. "pangoaguirre-learndependabot"

    class Config:
        extra = "forbid"


class TeamRegisterRequest(BaseModel):
    team_id: str
    name: str
    repository: str

    class Config:
        extra = "forbid"