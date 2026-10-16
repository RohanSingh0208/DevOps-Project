"""Service layer: business logic for Reservations."""

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Reservation, ReservationStatus
from app.schemas import ReservationCreate, ReservationUpdate
from app.services.resources import get_resource_availability


class OverlapError(Exception):
    """Raised when a reservation overlaps an existing active reservation."""


async def list_reservations(
    db: AsyncSession,
    resource_id: int | None = None,
    status: str | None = None,
    requester_email: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Reservation]:
    stmt = (
        select(Reservation)
        .options(selectinload(Reservation.resource))
        .order_by(Reservation.start_time.desc())
    )
    if resource_id:
        stmt = stmt.where(Reservation.resource_id == resource_id)
    if status:
        stmt = stmt.where(Reservation.status == status)
    if requester_email:
        stmt = stmt.where(Reservation.requester_email == requester_email)
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_reservation(db: AsyncSession, reservation_id: int) -> Reservation | None:
    stmt = (
        select(Reservation)
        .options(selectinload(Reservation.resource))
        .where(Reservation.id == reservation_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_reservation(db: AsyncSession, data: ReservationCreate) -> Reservation:
    available = await get_resource_availability(
        db, data.resource_id, data.start_time, data.end_time
    )
    if not available:
        raise OverlapError(
            f"Resource {data.resource_id} already has an active reservation "
            f"overlapping {data.start_time} – {data.end_time}"
        )
    reservation = Reservation(**data.model_dump())
    db.add(reservation)
    await db.flush()
    await db.refresh(reservation)
    return reservation


async def update_reservation(
    db: AsyncSession, reservation: Reservation, data: ReservationUpdate
) -> Reservation:
    update_data = data.model_dump(exclude_unset=True)

    # Re-validate availability if times changed
    new_start = update_data.get("start_time", reservation.start_time)
    new_end = update_data.get("end_time", reservation.end_time)
    if "start_time" in update_data or "end_time" in update_data:
        available = await get_resource_availability(
            db, reservation.resource_id, new_start, new_end, exclude_reservation_id=reservation.id
        )
        if not available:
            raise OverlapError(
                f"Resource {reservation.resource_id} already has an active reservation "
                f"overlapping {new_start} – {new_end}"
            )

    for field, value in update_data.items():
        setattr(reservation, field, value)
    await db.flush()
    await db.refresh(reservation)
    return reservation


async def delete_reservation(db: AsyncSession, reservation: Reservation) -> None:
    await db.delete(reservation)
    await db.flush()
