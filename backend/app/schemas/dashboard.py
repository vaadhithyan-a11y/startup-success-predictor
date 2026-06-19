from pydantic import BaseModel


class SimilarStartup(BaseModel):
    startup_id: int
    similarity_score: float


class DashboardResponse(BaseModel):
    rankings: list
    risk_distribution: dict
    funding_trends: list
    industry_analysis: dict
