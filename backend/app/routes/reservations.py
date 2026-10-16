"""REST routes for Reservations."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import ReservationCreate, ReservationResponse, ReservationUpdate
from app.services import reservations as svc
from app.services.reservations import OverlapError

router = APIRouter(prefix="/api/reservations", tags=["reservations"])


@router.get("", response_model=list[ReservationResponse])
async def list_reservations(
    resource_id: int | None = Query(None),
    status: str | None = Query(None),
    requester_email: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    return await svc.list_reservations(db, resource_id, status, requester_email, skip, limit)


@router.get("/{reservation_id}", response_model=ReservationResponse)
async def get_reservation(reservation_id: int, db: AsyncSession = Depends(get_db)):
    reservation = await svc.get_reservation(db, reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return reservation


@router.post("", response_model=ReservationResponse, status_code=201)
async def create_reservation(data: ReservationCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await svc.create_reservation(db, data)
    except OverlapError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.put("/{reservation_id}", response_model=ReservationResponse)
async def update_reservation(
    reservation_id: int, data: ReservationUpdate, db: AsyncSession = Depends(get_db)
):
    reservation = await svc.get_reservation(db, reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    try:
        return await svc.update_reservation(db, reservation, data)
    except OverlapError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.delete("/{reservation_id}", status_code=204)
async def delete_reservation(reservation_id: int, db: AsyncSession = Depends(get_db)):
    reservation = await svc.get_reservation(db, reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    await svc.delete_reservation(db, reservation)
