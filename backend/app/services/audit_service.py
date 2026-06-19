from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


class AuditService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def log(self, user_id: int, action: str, target_type: str | None = None,
                  target_id: int | None = None, details: dict | None = None) -> AuditLog:
        entry = AuditLog(
            user_id=user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=details,
            timestamp=datetime.now(timezone.utc),
        )
        self.db.add(entry)
        await self.db.flush()
        return entry

    async def get_logs(self, skip: int = 0, limit: int = 100) -> list[AuditLog]:
        from sqlalchemy import select
        result = await self.db.execute(
            select(AuditLog).order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit)
        )
        return list(result.scalars().all())
