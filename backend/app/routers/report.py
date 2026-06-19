from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.report import ReportGenerateRequest, ReportResponse
from app.services.report_service import ReportService

router = APIRouter(prefix="/report", tags=["Reports"])

service = ReportService()


@router.post("/generate", response_model=ReportResponse)
async def generate_report(
    request: ReportGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = service.generate_report(
        startup_name=f"Startup_{request.startup_id}",
        industry="Tech",
        revenue=5000000,
        employees=50,
        founder_experience=8,
        funding_raised=10000000,
        market_size=500000000,
        growth_rate=0.3,
        burn_rate=200000,
        customer_growth=0.2,
    )
    return ReportResponse(
        report_id=result["report_id"],
        pdf_url=result["pdf_url"],
        summary=result["summary"],
    )
