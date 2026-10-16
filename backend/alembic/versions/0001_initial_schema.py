"""Initial schema — create resources, reservations, maintenance_requests tables.

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── resources ────────────────────────────────────────────────────────
    op.create_table(
        "resources",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("resource_type", sa.String(length=50), nullable=False),
        sa.Column("location", sa.String(length=300), nullable=False),
        sa.Column("building", sa.String(length=100), nullable=True),
        sa.Column("capacity", sa.Integer(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="available"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("amenities", sa.Text(), nullable=True),
        sa.Column("image_url", sa.String(length=500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_resources_id"), "resources", ["id"], unique=False)
    op.create_index("ix_resources_type_status", "resources", ["resource_type", "status"])
    op.create_index("ix_resources_building", "resources", ["building"])

    # ── reservations ──────────────────────────────────────────────────────
    op.create_table(
        "reservations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("resource_id", sa.Integer(), nullable=False),
        sa.Column("requester_name", sa.String(length=200), nullable=False),
        sa.Column("requester_email", sa.String(length=254), nullable=False),
        sa.Column("requester_role", sa.String(length=50), nullable=False, server_default="student"),
        sa.Column("purpose", sa.Text(), nullable=False),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("attendees_count", sa.Integer(), nullable=True, server_default="1"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="pending"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["resource_id"], ["resources.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_reservations_id"), "reservations", ["id"], unique=False)
    op.create_index(
        "ix_reservations_resource_time",
        "reservations",
        ["resource_id", "start_time", "end_time"],
    )
    op.create_index("ix_reservations_status", "reservations", ["status"])
    op.create_index("ix_reservations_requester_email", "reservations", ["requester_email"])

    # ── maintenance_requests ──────────────────────────────────────────────
    op.create_table(
        "maintenance_requests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("resource_id", sa.Integer(), nullable=False),
        sa.Column("reported_by", sa.String(length=200), nullable=False),
        sa.Column("reporter_email", sa.String(length=254), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("priority", sa.String(length=20), nullable=False, server_default="medium"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="open"),
        sa.Column("resolution_notes", sa.Text(), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["resource_id"], ["resources.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_maintenance_requests_id"), "maintenance_requests", ["id"], unique=False
    )
    op.create_index(
        "ix_maintenance_resource_status",
        "maintenance_requests",
        ["resource_id", "status"],
    )
    op.create_index(
        "ix_maintenance_priority_status",
        "maintenance_requests",
        ["priority", "status"],
    )


def downgrade() -> None:
    op.drop_table("maintenance_requests")
    op.drop_table("reservations")
    op.drop_table("resources")
