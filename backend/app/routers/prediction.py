from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.prediction import (
    SuccessPredictionRequest, SuccessPredictionResponse,
    GrowthPredictionRequest, GrowthPredictionResponse,
    RiskPredictionRequest, RiskPredictionResponse,
)
from app.services.prediction_service import PredictionService

router = APIRouter(prefix="/predict", tags=["Predictions"])

service = PredictionService()


@router.post("/success", response_model=SuccessPredictionResponse)
async def predict_success(
    request: SuccessPredictionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.predict_success(
        industry=request.industry,
        revenue=request.revenue,
        employees=request.employees,
        founder_experience=request.founder_experience,
        funding_raised=request.funding_raised,
        market_size=request.market_size,
        customer_growth=request.customer_growth,
    )


@router.post("/growth", response_model=GrowthPredictionResponse)
async def predict_growth(
    request: GrowthPredictionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.predict_growth(
        revenue=request.revenue,
        employees=request.employees,
        funding_raised=request.funding_raised,
        market_size=request.market_size,
        growth_rate=request.growth_rate,
    )


@router.post("/risk", response_model=RiskPredictionResponse)
async def predict_risk(
    request: RiskPredictionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.predict_risk(
        industry=request.industry,
        revenue=request.revenue,
        employees=request.employees,
        founder_experience=request.founder_experience,
        funding_raised=request.funding_raised,
        market_size=request.market_size,
        growth_rate=request.growth_rate,
        burn_rate=request.burn_rate,
    )
