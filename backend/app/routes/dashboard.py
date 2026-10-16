"""Dashboard statistics route."""

from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import MaintenanceRequest, MaintenancePriority, MaintenanceStatus
from app.models import Reservation, ReservationStatus
from app.models import Resource, ResourceStatus
from app.schemas import DashboardStats, MaintenanceResponse, ReservationResponse

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    # ── Resource counts ───────────────────────────────────────────────────
    total_res = await db.execute(select(func.count(Resource.id)))
    avail_res = await db.execute(
        select(func.count(Resource.id)).where(Resource.status == ResourceStatus.AVAILABLE)
    )
    maint_res = await db.execute(
        select(func.count(Resource.id)).where(Resource.status == ResourceStatus.UNDER_MAINTENANCE)
    )

    # ── Reservation counts ────────────────────────────────────────────────
    total_rsv = await db.execute(select(func.count(Reservation.id)))
    pending_rsv = await db.execute(
        select(func.count(Reservation.id)).where(
            Reservation.status == ReservationStatus.PENDING
        )
    )
    confirmed_rsv = await db.execute(
        select(func.count(Reservation.id)).where(
            Reservation.status == ReservationStatus.CONFIRMED
        )
    )

    # ── Maintenance counts ────────────────────────────────────────────────
    open_maint = await db.execute(
        select(func.count(MaintenanceRequest.id)).where(
            MaintenanceRequest.status == MaintenanceStatus.OPEN
        )
    )
    critical_maint = await db.execute(
        select(func.count(MaintenanceRequest.id)).where(
            MaintenanceRequest.priority == MaintenancePriority.CRITICAL,
            MaintenanceRequest.status.notin_(
                [MaintenanceStatus.RESOLVED, MaintenanceStatus.CLOSED]
            ),
        )
    )

    # ── Resources by type ─────────────────────────────────────────────────
    type_rows = await db.execute(
        select(Resource.resource_type, func.count(Resource.id)).group_by(Resource.resource_type)
    )
    resources_by_type = {row[0]: row[1] for row in type_rows.all()}

    # ── Recent reservations (last 5) ───────────────────────────────────────
    recent_rsv_q = await db.execute(
        select(Reservation)
        .options(selectinload(Reservation.resource))
        .order_by(Reservation.created_at.desc())
        .limit(5)
    )
    recent_reservations = [
        ReservationResponse.model_validate(r) for r in recent_rsv_q.scalars().all()
    ]

    # ── Recent maintenance (last 5) ────────────────────────────────────────
    recent_maint_q = await db.execute(
        select(MaintenanceRequest)
        .options(selectinload(MaintenanceRequest.resource))
        .order_by(MaintenanceRequest.created_at.desc())
        .limit(5)
    )
    recent_maintenance = [
        MaintenanceResponse.model_validate(m) for m in recent_maint_q.scalars().all()
    ]

    return DashboardStats(
        total_resources=total_res.scalar_one() or 0,
        available_resources=avail_res.scalar_one() or 0,
        under_maintenance_resources=maint_res.scalar_one() or 0,
        total_reservations=total_rsv.scalar_one() or 0,
        pending_reservations=pending_rsv.scalar_one() or 0,
        confirmed_reservations=confirmed_rsv.scalar_one() or 0,
        open_maintenance_requests=open_maint.scalar_one() or 0,
        critical_maintenance_requests=critical_maint.scalar_one() or 0,
        resources_by_type=resources_by_type,
        recent_reservations=recent_reservations,
        recent_maintenance=recent_maintenance,
    )
