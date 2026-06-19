from pydantic import BaseModel


class SuccessPredictionRequest(BaseModel):
    industry: str
    revenue: float
    employees: int
    founder_experience: float
    funding_raised: float
    market_size: float
    customer_growth: float


class GrowthPredictionRequest(BaseModel):
    revenue: float
    employees: int
    funding_raised: float
    market_size: float
    growth_rate: float


class RiskPredictionRequest(BaseModel):
    industry: str
    revenue: float
    employees: int
    founder_experience: float
    funding_raised: float
    market_size: float
    growth_rate: float
    burn_rate: float


class SuccessPredictionResponse(BaseModel):
    success_probability: float
    model_version: str


class GrowthPredictionResponse(BaseModel):
    growth_1y: float
    growth_3y: float
    growth_5y: float
    model_version: str


class RiskPredictionResponse(BaseModel):
    financial_risk: float
    operational_risk: float
    market_risk: float
    team_risk: float
    risk_score: float
