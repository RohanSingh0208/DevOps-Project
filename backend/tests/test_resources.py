"""Tests: Resource CRUD API endpoints."""

import pytest


RESOURCE_PAYLOAD = {
    "name": "Computer Lab A",
    "resource_type": "laboratory",
    "location": "Block A, Room 101",
    "building": "Block A",
    "capacity": 40,
    "description": "Equipped with 40 workstations",
    "status": "available",
    "is_active": True,
}


# ── CREATE ────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_resource_success(client):
    response = await client.post("/api/resources", json=RESOURCE_PAYLOAD)
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Computer Lab A"
    assert body["resource_type"] == "laboratory"
    assert body["id"] is not None


@pytest.mark.asyncio
async def test_create_resource_missing_required_field(client):
    """Submitting without 'name' should return 422 Unprocessable Entity."""
    payload = {**RESOURCE_PAYLOAD}
    del payload["name"]
    response = await client.post("/api/resources", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_resource_invalid_type(client):
    """An invalid enum value for resource_type must fail validation."""
    payload = {**RESOURCE_PAYLOAD, "resource_type": "swimming_pool"}
    response = await client.post("/api/resources", json=payload)
    assert response.status_code == 422


# ── READ ──────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_resource_not_found(client):
    response = await client.get("/api/resources/9999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_list_resources_initially_empty(client):
    response = await client.get("/api/resources")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_and_retrieve_resource(client):
    # Create resource first
    create_response = await client.post("/api/resources", json=RESOURCE_PAYLOAD)
    assert create_response.status_code == 201
    created_id = create_response.json()["id"]

    # List — should appear
    list_response = await client.get("/api/resources")
    assert list_response.status_code == 200
    ids = [r["id"] for r in list_response.json()]
    assert created_id in ids

    # Retrieve by ID
    get_response = await client.get(f"/api/resources/{created_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == created_id


# ── UPDATE ────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_resource(client):
    create_response = await client.post("/api/resources", json=RESOURCE_PAYLOAD)
    resource_id = create_response.json()["id"]

    update_response = await client.put(
        f"/api/resources/{resource_id}",
        json={"status": "under_maintenance", "description": "AC repair in progress"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "under_maintenance"


@pytest.mark.asyncio
async def test_update_nonexistent_resource(client):
    response = await client.put("/api/resources/9999", json={"name": "Ghost Room"})
    assert response.status_code == 404


# ── DELETE ────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_delete_resource(client):
    create_response = await client.post("/api/resources", json=RESOURCE_PAYLOAD)
    resource_id = create_response.json()["id"]

    delete_response = await client.delete(f"/api/resources/{resource_id}")
    assert delete_response.status_code == 204

    get_response = await client.get(f"/api/resources/{resource_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_nonexistent_resource(client):
    response = await client.delete("/api/resources/9999")
    assert response.status_code == 404


# ── FILTERING ─────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_filter_resources_by_type(client):
    await client.post("/api/resources", json={**RESOURCE_PAYLOAD, "resource_type": "classroom"})
    await client.post("/api/resources", json={**RESOURCE_PAYLOAD, "name": "Meeting Room B", "resource_type": "meeting_room"})

    response = await client.get("/api/resources?resource_type=classroom")
    assert response.status_code == 200
    for r in response.json():
        assert r["resource_type"] == "classroom"
