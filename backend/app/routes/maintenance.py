"""REST routes for Maintenance Requests."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import MaintenanceCreate, MaintenanceResponse, MaintenanceUpdate
from app.services import maintenance as svc

router = APIRouter(prefix="/api/maintenance", tags=["maintenance"])


@router.get("", response_model=list[MaintenanceResponse])
async def list_maintenance(
    resource_id: int | None = Query(None),
    status: str | None = Query(None),
    priority: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    return await svc.list_maintenance(db, resource_id, status, priority, skip, limit)


@router.get("/{maintenance_id}", response_model=MaintenanceResponse)
async def get_maintenance(maintenance_id: int, db: AsyncSession = Depends(get_db)):
    mr = await svc.get_maintenance(db, maintenance_id)
    if not mr:
        raise HTTPException(status_code=404, detail="Maintenance request not found")
    return mr


@router.post("", response_model=MaintenanceResponse, status_code=201)
async def create_maintenance(data: MaintenanceCreate, db: AsyncSession = Depends(get_db)):
    return await svc.create_maintenance(db, data)


@router.put("/{maintenance_id}", response_model=MaintenanceResponse)
async def update_maintenance(
    maintenance_id: int, data: MaintenanceUpdate, db: AsyncSession = Depends(get_db)
):
    mr = await svc.get_maintenance(db, maintenance_id)
    if not mr:
        raise HTTPException(status_code=404, detail="Maintenance request not found")
    return await svc.update_maintenance(db, mr, data)


@router.delete("/{maintenance_id}", status_code=204)
async def delete_maintenance(maintenance_id: int, db: AsyncSession = Depends(get_db)):
    mr = await svc.get_maintenance(db, maintenance_id)
    if not mr:
        raise HTTPException(status_code=404, detail="Maintenance request not found")
    await svc.delete_maintenance(db, mr)
