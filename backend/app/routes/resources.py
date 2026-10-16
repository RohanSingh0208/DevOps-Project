"""REST routes for Resources."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import ResourceCreate, ResourceResponse, ResourceUpdate
from app.services import resources as svc

router = APIRouter(prefix="/api/resources", tags=["resources"])


@router.get("", response_model=list[ResourceResponse])
async def list_resources(
    resource_type: str | None = Query(None),
    status: str | None = Query(None),
    building: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    return await svc.list_resources(db, resource_type, status, building, skip, limit)


@router.get("/{resource_id}", response_model=ResourceResponse)
async def get_resource(resource_id: int, db: AsyncSession = Depends(get_db)):
    resource = await svc.get_resource(db, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource


@router.post("", response_model=ResourceResponse, status_code=201)
async def create_resource(data: ResourceCreate, db: AsyncSession = Depends(get_db)):
    return await svc.create_resource(db, data)


@router.put("/{resource_id}", response_model=ResourceResponse)
async def update_resource(
    resource_id: int, data: ResourceUpdate, db: AsyncSession = Depends(get_db)
):
    resource = await svc.get_resource(db, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return await svc.update_resource(db, resource, data)


@router.delete("/{resource_id}", status_code=204)
async def delete_resource(resource_id: int, db: AsyncSession = Depends(get_db)):
    resource = await svc.get_resource(db, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    await svc.delete_resource(db, resource)
