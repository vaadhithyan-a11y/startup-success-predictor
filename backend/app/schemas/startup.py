from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class StartupCreate(BaseModel):
    founder_id: int
    name: str
    industry: str
    location: Optional[str] = None
    founding_year: Optional[int] = None
    description: Optional[str] = None


class StartupUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    founding_year: Optional[int] = None
    description: Optional[str] = None


class StartupResponse(BaseModel):
    id: int
    founder_id: int
    name: str
    industry: str
    location: Optional[str] = None
    founding_year: Optional[int] = None
    description: Optional[str] = None
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class StartupListResponse(BaseModel):
    id: int
    data: StartupResponse
