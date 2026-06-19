from fastapi import APIRouter, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.similarity_service import SimilarityService
from app.services.dashboard_service import DashboardService
from app.schemas.dashboard import DashboardResponse, SimilarStartup

router = APIRouter(tags=["Dashboard"])
similarity_service = SimilarityService()
dashboard_service = DashboardService()


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return dashboard_service.get_dashboard_data()


@router.get("/similar", response_model=list[SimilarStartup])
async def get_similar(
    startup_id: int = Query(..., description="Startup ID"),
    n: int = Query(5, description="Number of similar startups"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return similarity_service.find_similar(startup_id, n)
