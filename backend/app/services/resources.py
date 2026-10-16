"""Service layer: business logic for Resources."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Resource, Reservation, ReservationStatus
from app.schemas import ResourceCreate, ResourceUpdate


async def list_resources(
    db: AsyncSession,
    resource_type: str | None = None,
    status: str | None = None,
    building: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Resource]:
    stmt = select(Resource).where(Resource.is_active)
    if resource_type:
        stmt = stmt.where(Resource.resource_type == resource_type)
    if status:
        stmt = stmt.where(Resource.status == status)
    if building:
        stmt = stmt.where(Resource.building.ilike(f"%{building}%"))
    stmt = stmt.offset(skip).limit(limit).order_by(Resource.name)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_resource(db: AsyncSession, resource_id: int) -> Resource | None:
    result = await db.execute(select(Resource).where(Resource.id == resource_id))
    return result.scalar_one_or_none()


async def create_resource(db: AsyncSession, data: ResourceCreate) -> Resource:
    resource = Resource(**data.model_dump())
    db.add(resource)
    await db.flush()
    await db.refresh(resource)
    return resource


async def update_resource(
    db: AsyncSession, resource: Resource, data: ResourceUpdate
) -> Resource:
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(resource, field, value)
    await db.flush()
    await db.refresh(resource)
    return resource


async def delete_resource(db: AsyncSession, resource: Resource) -> None:
    await db.delete(resource)
    await db.flush()


async def get_resource_availability(
    db: AsyncSession,
    resource_id: int,
    start_time,
    end_time,
    exclude_reservation_id: int | None = None,
) -> bool:
    """Return True if the resource has no overlapping confirmed/pending reservation."""
    stmt = select(func.count(Reservation.id)).where(
        Reservation.resource_id == resource_id,
        Reservation.status.in_([ReservationStatus.CONFIRMED, ReservationStatus.PENDING]),
        Reservation.start_time < end_time,
        Reservation.end_time > start_time,
    )
    if exclude_reservation_id:
        stmt = stmt.where(Reservation.id != exclude_reservation_id)
    result = await db.execute(stmt)
    return (result.scalar_one() or 0) == 0
