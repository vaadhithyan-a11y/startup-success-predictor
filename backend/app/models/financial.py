from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, func
from app.core.database import Base


class Financial(Base):
    __tablename__ = "financials"

    id = Column(Integer, primary_key=True, index=True)
    startup_id = Column(Integer, ForeignKey("startups.id"), nullable=False, index=True)
    revenue = Column(Float, nullable=True)
    funding_raised = Column(Float, nullable=True)
    employees = Column(Integer, nullable=True)
    burn_rate = Column(Float, nullable=True)
    market_size = Column(Float, nullable=True)
    growth_rate = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
