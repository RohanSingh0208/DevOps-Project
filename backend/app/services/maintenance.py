"""Service layer: business logic for Maintenance Requests."""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import MaintenanceRequest, MaintenanceStatus
from app.schemas import MaintenanceCreate, MaintenanceUpdate


async def list_maintenance(
    db: AsyncSession,
    resource_id: int | None = None,
    status: str | None = None,
    priority: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[MaintenanceRequest]:
    stmt = (
        select(MaintenanceRequest)
        .options(selectinload(MaintenanceRequest.resource))
        .order_by(MaintenanceRequest.created_at.desc())
    )
    if resource_id:
        stmt = stmt.where(MaintenanceRequest.resource_id == resource_id)
    if status:
        stmt = stmt.where(MaintenanceRequest.status == status)
    if priority:
        stmt = stmt.where(MaintenanceRequest.priority == priority)
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_maintenance(db: AsyncSession, maintenance_id: int) -> MaintenanceRequest | None:
    stmt = (
        select(MaintenanceRequest)
        .options(selectinload(MaintenanceRequest.resource))
        .where(MaintenanceRequest.id == maintenance_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_maintenance(db: AsyncSession, data: MaintenanceCreate) -> MaintenanceRequest:
    mr = MaintenanceRequest(**data.model_dump())
    db.add(mr)
    await db.flush()
    await db.refresh(mr)
    return mr


async def update_maintenance(
    db: AsyncSession, mr: MaintenanceRequest, data: MaintenanceUpdate
) -> MaintenanceRequest:
    update_data = data.model_dump(exclude_unset=True)

    # Automatically set resolved_at timestamp when transitioning to resolved
    if update_data.get("status") == MaintenanceStatus.RESOLVED and not mr.resolved_at:
        mr.resolved_at = datetime.now(timezone.utc)

    for field, value in update_data.items():
        setattr(mr, field, value)
    await db.flush()
    await db.refresh(mr)
    return mr


async def delete_maintenance(db: AsyncSession, mr: MaintenanceRequest) -> None:
    await db.delete(mr)
    await db.flush()
