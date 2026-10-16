"""Tests: Reservation API including time validation and overlap prevention."""

from datetime import datetime, timedelta, timezone

import pytest

RESOURCE_PAYLOAD = {
    "name": "Seminar Hall",
    "resource_type": "classroom",
    "location": "Block B, Ground Floor",
    "building": "Block B",
    "capacity": 100,
    "status": "available",
    "is_active": True,
}


def make_reservation_payload(resource_id: int, offset_hours: int = 0) -> dict:
    base = datetime(2025, 6, 15, 9, 0, tzinfo=timezone.utc) + timedelta(hours=offset_hours)
    return {
        "resource_id": resource_id,
        "requester_name": "Alice Johnson",
        "requester_email": "alice@university.edu",
        "requester_role": "student",
        "purpose": "Study group session",
        "start_time": base.isoformat(),
        "end_time": (base + timedelta(hours=2)).isoformat(),
        "attendees_count": 10,
    }


@pytest.fixture
async def resource_id(client) -> int:
    response = await client.post("/api/resources", json=RESOURCE_PAYLOAD)
    assert response.status_code == 201
    return response.json()["id"]


# ── CREATE ────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_reservation_success(client, resource_id):
    payload = make_reservation_payload(resource_id)
    response = await client.post("/api/reservations", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "pending"
    assert body["resource_id"] == resource_id


@pytest.mark.asyncio
async def test_create_reservation_end_before_start(client, resource_id):
    """end_time before start_time must return 422."""
    base = datetime(2025, 6, 15, 9, 0, tzinfo=timezone.utc)
    payload = {
        "resource_id": resource_id,
        "requester_name": "Bob Smith",
        "requester_email": "bob@university.edu",
        "purpose": "Invalid booking",
        "start_time": base.isoformat(),
        "end_time": (base - timedelta(hours=1)).isoformat(),
    }
    response = await client.post("/api/reservations", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_overlapping_reservation_rejected(client, resource_id):
    """A second reservation overlapping an existing confirmed/pending one must return 409."""
    payload = make_reservation_payload(resource_id)

    # First reservation succeeds
    first = await client.post("/api/reservations", json=payload)
    assert first.status_code == 201

    # Second reservation with same time overlaps → conflict
    second = await client.post("/api/reservations", json=payload)
    assert second.status_code == 409
    assert "overlap" in second.json()["detail"].lower() or "active reservation" in second.json()["detail"].lower()


@pytest.mark.asyncio
async def test_non_overlapping_reservations_allowed(client, resource_id):
    """Two non-overlapping reservations for the same resource must both succeed."""
    payload1 = make_reservation_payload(resource_id, offset_hours=0)   # 09:00 – 11:00
    payload2 = make_reservation_payload(resource_id, offset_hours=2)   # 11:00 – 13:00

    r1 = await client.post("/api/reservations", json=payload1)
    r2 = await client.post("/api/reservations", json=payload2)
    assert r1.status_code == 201
    assert r2.status_code == 201


# ── READ ──────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_reservation_not_found(client):
    response = await client.get("/api/reservations/9999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_reservations(client, resource_id):
    payload = make_reservation_payload(resource_id)
    await client.post("/api/reservations", json=payload)

    response = await client.get("/api/reservations")
    assert response.status_code == 200
    assert len(response.json()) >= 1


# ── UPDATE ────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_reservation_status(client, resource_id):
    payload = make_reservation_payload(resource_id)
    create_resp = await client.post("/api/reservations", json=payload)
    reservation_id = create_resp.json()["id"]

    update_resp = await client.put(
        f"/api/reservations/{reservation_id}", json={"status": "confirmed"}
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "confirmed"


# ── DELETE ────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_delete_reservation(client, resource_id):
    payload = make_reservation_payload(resource_id)
    create_resp = await client.post("/api/reservations", json=payload)
    reservation_id = create_resp.json()["id"]

    delete_resp = await client.delete(f"/api/reservations/{reservation_id}")
    assert delete_resp.status_code == 204

    get_resp = await client.get(f"/api/reservations/{reservation_id}")
    assert get_resp.status_code == 404
