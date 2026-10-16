"""Pydantic schemas for request validation and response serialization."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, model_validator

from app.models import (
    MaintenancePriority,
    MaintenanceStatus,
    ReservationStatus,
    ResourceStatus,
    ResourceType,
)


# ─── Resource Schemas ─────────────────────────────────────────────────────────


class ResourceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    resource_type: ResourceType
    location: str = Field(..., min_length=1, max_length=300)
    building: Optional[str] = Field(None, max_length=100)
    capacity: Optional[int] = Field(None, ge=1, le=10000)
    description: Optional[str] = None
    status: ResourceStatus = ResourceStatus.AVAILABLE
    is_active: bool = True
    amenities: Optional[str] = None
    image_url: Optional[str] = Field(None, max_length=500)


class ResourceCreate(ResourceBase):
    pass


class ResourceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    resource_type: Optional[ResourceType] = None
    location: Optional[str] = Field(None, min_length=1, max_length=300)
    building: Optional[str] = Field(None, max_length=100)
    capacity: Optional[int] = Field(None, ge=1, le=10000)
    description: Optional[str] = None
    status: Optional[ResourceStatus] = None
    is_active: Optional[bool] = None
    amenities: Optional[str] = None
    image_url: Optional[str] = Field(None, max_length=500)


class ResourceResponse(ResourceBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ─── Reservation Schemas ──────────────────────────────────────────────────────


class ReservationBase(BaseModel):
    resource_id: int
    requester_name: str = Field(..., min_length=1, max_length=200)
    requester_email: EmailStr
    requester_role: str = Field(default="student", max_length=50)
    purpose: str = Field(..., min_length=1)
    start_time: datetime
    end_time: datetime
    attendees_count: Optional[int] = Field(None, ge=1)
    notes: Optional[str] = None

    @model_validator(mode="after")
    def validate_times(self) -> "ReservationBase":
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self


class ReservationCreate(ReservationBase):
    pass


class ReservationUpdate(BaseModel):
    requester_name: Optional[str] = Field(None, min_length=1, max_length=200)
    requester_email: Optional[EmailStr] = None
    requester_role: Optional[str] = Field(None, max_length=50)
    purpose: Optional[str] = Field(None, min_length=1)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    attendees_count: Optional[int] = Field(None, ge=1)
    status: Optional[ReservationStatus] = None
    notes: Optional[str] = None

    @model_validator(mode="after")
    def validate_times(self) -> "ReservationUpdate":
        if self.start_time and self.end_time and self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self


class ReservationResponse(ReservationBase):
    id: int
    status: ReservationStatus
    resource: Optional[ResourceResponse] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ─── Maintenance Schemas ──────────────────────────────────────────────────────


class MaintenanceBase(BaseModel):
    resource_id: int
    reported_by: str = Field(..., min_length=1, max_length=200)
    reporter_email: EmailStr
    title: str = Field(..., min_length=1, max_length=300)
    description: str = Field(..., min_length=1)
    priority: MaintenancePriority = MaintenancePriority.MEDIUM


class MaintenanceCreate(MaintenanceBase):
    pass


class MaintenanceUpdate(BaseModel):
    reported_by: Optional[str] = Field(None, min_length=1, max_length=200)
    reporter_email: Optional[EmailStr] = None
    title: Optional[str] = Field(None, min_length=1, max_length=300)
    description: Optional[str] = Field(None, min_length=1)
    priority: Optional[MaintenancePriority] = None
    status: Optional[MaintenanceStatus] = None
    resolution_notes: Optional[str] = None


class MaintenanceResponse(MaintenanceBase):
    id: int
    status: MaintenanceStatus
    resolution_notes: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resource: Optional[ResourceResponse] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ─── Dashboard Schemas ────────────────────────────────────────────────────────


class DashboardStats(BaseModel):
    total_resources: int
    available_resources: int
    under_maintenance_resources: int
    total_reservations: int
    pending_reservations: int
    confirmed_reservations: int
    open_maintenance_requests: int
    critical_maintenance_requests: int
    resources_by_type: dict[str, int]
    recent_reservations: list[ReservationResponse]
    recent_maintenance: list[MaintenanceResponse]
