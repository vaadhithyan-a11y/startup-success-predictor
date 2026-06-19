from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_admin
from app.models.user import User
from app.schemas.startup import StartupCreate, StartupUpdate, StartupResponse
from app.services.startup_service import StartupService

router = APIRouter(prefix="/startup", tags=["Startups"])


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_startup(
    data: StartupCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = StartupService(db)
    startup = await service.create(data)
    return {"startup_id": startup.id, "message": "Startup created successfully"}


@router.get("/{startup_id}", response_model=dict)
async def get_startup(
    startup_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = StartupService(db)
    startup = await service.get_by_id(startup_id)
    if not startup:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Startup not found")
    return {"id": startup.id, "data": StartupResponse.model_validate(startup).model_dump()}


@router.put("/{startup_id}", response_model=dict)
async def update_startup(
    startup_id: int,
    data: StartupUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    service = StartupService(db)
    count = await service.update(startup_id, data)
    return {"updated_count": count}


@router.delete("/{startup_id}", response_model=dict)
async def delete_startup(
    startup_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    service = StartupService(db)
    deleted = await service.soft_delete(startup_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Startup not found")
    return {"deleted": True}
