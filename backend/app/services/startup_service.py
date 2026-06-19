from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.startup import Startup
from app.schemas.startup import StartupCreate, StartupUpdate


class StartupService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: StartupCreate) -> Startup:
        startup = Startup(**data.model_dump())
        self.db.add(startup)
        await self.db.flush()
        return startup

    async def get_by_id(self, startup_id: int) -> Startup | None:
        result = await self.db.execute(
            select(Startup).where(Startup.id == startup_id, Startup.is_deleted.is_(False))
        )
        return result.scalar_one_or_none()

    async def update(self, startup_id: int, data: StartupUpdate) -> int:
        result = await self.db.execute(
            select(Startup).where(Startup.id == startup_id, Startup.is_deleted.is_(False))
        )
        startup = result.scalar_one_or_none()
        if not startup:
            return 0
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(startup, key, value)
        await self.db.flush()
        return 1

    async def soft_delete(self, startup_id: int) -> bool:
        result = await self.db.execute(
            select(Startup).where(Startup.id == startup_id, Startup.is_deleted.is_(False))
        )
        startup = result.scalar_one_or_none()
        if not startup:
            return False
        startup.is_deleted = True
        await self.db.flush()
        return True

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[Startup]:
        result = await self.db.execute(
            select(Startup).where(Startup.is_deleted.is_(False)).offset(skip).limit(limit)
        )
        return list(result.scalars().all())
