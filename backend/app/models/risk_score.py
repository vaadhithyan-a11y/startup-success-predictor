from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, func
from app.core.database import Base


class RiskScore(Base):
    __tablename__ = "risk_scores"

    id = Column(Integer, primary_key=True, index=True)
    startup_id = Column(Integer, ForeignKey("startups.id"), nullable=False, index=True)
    financial_risk = Column(Float, nullable=True)
    operational_risk = Column(Float, nullable=True)
    market_risk = Column(Float, nullable=True)
    team_risk = Column(Float, nullable=True)
    risk_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
