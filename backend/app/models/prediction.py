from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, func
from app.core.database import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    startup_id = Column(Integer, ForeignKey("startups.id"), nullable=False, index=True)
    success_probability = Column(Float, nullable=True)
    growth_1y = Column(Float, nullable=True)
    growth_3y = Column(Float, nullable=True)
    growth_5y = Column(Float, nullable=True)
    risk_score = Column(Float, nullable=True)
    health_score = Column(Float, nullable=True)
    model_version = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
