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

    @property
    def _rescan_col(self):
        return _client[settings.mongo_db_name]["rescans"]

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

    async def save_rescan_user(self, alert_id: str, user_id: str, guild_id: str) -> None:
        await self._rescan_col.update_one(
            {"alert_id": alert_id},
            {"$set": {"alert_id": alert_id, "user_id": user_id, "guild_id": guild_id}},
            upsert=True,
        )

    async def consume_rescan_user(self, alert_id: str) -> str | None:
        doc = await self._rescan_col.find_one_and_delete({"alert_id": alert_id}, {"_id": 0})
        return doc["user_id"] if doc else None


repo = MongoTeamRepository()