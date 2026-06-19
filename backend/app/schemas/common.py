from pydantic import BaseModel
from typing import Optional, Any


class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    error_code: str
    data: Optional[Any] = None


class HealthResponse(BaseModel):
    status: str
    uptime: str
    version: str
