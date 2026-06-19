from fastapi import APIRouter
from app.core.config import settings
from app.schemas.common import HealthResponse
import time

router = APIRouter(tags=["Health"])
start_time = time.time()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    uptime_seconds = int(time.time() - start_time)
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime_str = f"{hours}h {minutes}m {seconds}s"
    return HealthResponse(status="ok", uptime=uptime_str, version=settings.app_version)
