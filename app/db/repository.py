from app.models.team import Team


class InMemoryTeamRepository:
    def __init__(self):
        self._by_repo: dict[str, Team] = {}  # repository → Team

    async def save(self, team: Team) -> None:
        self._by_repo[team.repository] = team

    async def get_by_repository(self, repository: str) -> Team | None:
        return self._by_repo.get(repository)

    async def delete(self, repository: str) -> None:
        self._by_repo.pop(repository, None)

    async def list_all(self) -> list[Team]:
        return list(self._by_repo.values())


repo = InMemoryTeamRepository()