from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, func
from app.core.database import Base


class Startup(Base):
    __tablename__ = "startups"

    id = Column(Integer, primary_key=True, index=True)
    founder_id = Column(Integer, ForeignKey("founders.id"), nullable=False)
    name = Column(String(255), nullable=False)
    industry = Column(String(255), nullable=False, index=True)
    location = Column(String(255), nullable=True, index=True)
    founding_year = Column(Integer, nullable=True)
    description = Column(String(2000), nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
