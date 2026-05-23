from motor.motor_asyncio import AsyncIOMotorClient
from app.models.team import Team
from app.config import settings

_client: AsyncIOMotorClient = None


async def connect():
    global _client
    _client = AsyncIOMotorClient(settings.mongo_uri)


async def disconnect():
    global _client
    if _client:
        _client.close()


class MongoTeamRepository:
    @property
    def _col(self):
        return _client[settings.mongo_db_name]["teams"]

    async def save(self, team: Team) -> None:
        await self._col.update_one(
            {"repository": team.repository},
            {"$set": team.model_dump()},
            upsert=True,
        )

    async def get_by_repository(self, repository: str) -> Team | None:
        doc = await self._col.find_one({"repository": repository}, {"_id": 0})
        return Team(**doc) if doc else None

    async def delete(self, repository: str) -> None:
        await self._col.delete_one({"repository": repository})

    async def list_all(self) -> list[Team]:
        cursor = self._col.find({}, {"_id": 0})
        return [Team(**doc) async for doc in cursor]


repo = MongoTeamRepository()