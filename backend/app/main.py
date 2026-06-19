from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.middleware import setup_middleware
from app.routers import auth, startup, health, prediction, report, dashboard

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

setup_middleware(app)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": str(exc), "error_code": "INTERNAL_ERROR", "data": None},
    )


app.include_router(auth.router)
app.include_router(startup.router)
app.include_router(health.router)
app.include_router(prediction.router)
app.include_router(report.router)
app.include_router(dashboard.router)
