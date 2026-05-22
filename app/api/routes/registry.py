from fastapi import APIRouter, HTTPException, status
from app.models.team import Team, TeamRegisterRequest
from app.db.repository import repo

router = APIRouter(prefix="/teams", tags=["registry"])


@router.post("/", response_model=Team, status_code=status.HTTP_201_CREATED)
async def register_team(request: TeamRegisterRequest):
    team = Team(**request.model_dump())
    await repo.save(team)
    return team


@router.delete("/{repository}", status_code=status.HTTP_204_NO_CONTENT)
async def deregister_team(repository: str):
    team = await repo.get_by_repository(repository)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    await repo.delete(repository)


@router.get("/", response_model=list[Team])
async def list_teams():
    return await repo.list_all()