"""SQLAlchemy ORM models for the Campus Resource Hub."""

from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# ─── Enumerations ────────────────────────────────────────────────────────────


class ResourceType(str, Enum):
    CLASSROOM = "classroom"
    LABORATORY = "laboratory"
    MEETING_ROOM = "meeting_room"
    PROJECTOR = "projector"
    EQUIPMENT = "equipment"
    SPORTS_FACILITY = "sports_facility"
    LIBRARY_ROOM = "library_room"


class ResourceStatus(str, Enum):
    AVAILABLE = "available"
    UNDER_MAINTENANCE = "under_maintenance"
    RESERVED = "reserved"
    INACTIVE = "inactive"


class ReservationStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class MaintenancePriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MaintenanceStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


# ─── Models ──────────────────────────────────────────────────────────────────


class Resource(Base):
    __tablename__ = "resources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)
    location: Mapped[str] = mapped_column(String(300), nullable=False)
    building: Mapped[str] = mapped_column(String(100), nullable=True)
    capacity: Mapped[int] = mapped_column(Integer, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default=ResourceStatus.AVAILABLE)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    amenities: Mapped[str] = mapped_column(Text, nullable=True)  # JSON string of amenity list
    image_url: Mapped[str] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    reservations: Mapped[list["Reservation"]] = relationship(
        "Reservation", back_populates="resource", cascade="all, delete-orphan"
    )
    maintenance_requests: Mapped[list["MaintenanceRequest"]] = relationship(
        "MaintenanceRequest", back_populates="resource", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_resources_type_status", "resource_type", "status"),
        Index("ix_resources_building", "building"),
    )


class Reservation(Base):
    __tablename__ = "reservations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    resource_id: Mapped[int] = mapped_column(Integer, ForeignKey("resources.id"), nullable=False)
    requester_name: Mapped[str] = mapped_column(String(200), nullable=False)
    requester_email: Mapped[str] = mapped_column(String(254), nullable=False)
    requester_role: Mapped[str] = mapped_column(String(50), nullable=False, default="student")
    purpose: Mapped[str] = mapped_column(Text, nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    attendees_count: Mapped[int] = mapped_column(Integer, nullable=True, default=1)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default=ReservationStatus.PENDING
    )
    notes: Mapped[str] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    resource: Mapped["Resource"] = relationship(
        "Resource", back_populates="reservations", lazy="selectin"
    )

    __table_args__ = (
        Index("ix_reservations_resource_time", "resource_id", "start_time", "end_time"),
        Index("ix_reservations_status", "status"),
        Index("ix_reservations_requester_email", "requester_email"),
    )


class MaintenanceRequest(Base):
    __tablename__ = "maintenance_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    resource_id: Mapped[int] = mapped_column(Integer, ForeignKey("resources.id"), nullable=False)
    reported_by: Mapped[str] = mapped_column(String(200), nullable=False)
    reporter_email: Mapped[str] = mapped_column(String(254), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(
        String(20), nullable=False, default=MaintenancePriority.MEDIUM
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default=MaintenanceStatus.OPEN
    )
    resolution_notes: Mapped[str] = mapped_column(Text, nullable=True)
    resolved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    resource: Mapped["Resource"] = relationship(
        "Resource", back_populates="maintenance_requests", lazy="selectin"
    )

    __table_args__ = (
        Index("ix_maintenance_resource_status", "resource_id", "status"),
        Index("ix_maintenance_priority_status", "priority", "status"),
    )
