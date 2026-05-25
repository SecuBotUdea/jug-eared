from pydantic import BaseModel


class Team(BaseModel):
    team_id: str
    name: str
    repository: str       # ej. "pangoaguirre-learndependabot"
    github_token: str     # token del repo para trigger_analyzer

    class Config:
        extra = "forbid"


class TeamRegisterRequest(BaseModel):
    team_id: str
    name: str
    repository: str
    github_token: str

    class Config:
        extra = "forbid"