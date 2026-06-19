from pydantic import BaseModel


class ReportGenerateRequest(BaseModel):
    startup_id: int


class ReportResponse(BaseModel):
    report_id: int
    pdf_url: str
    summary: dict
