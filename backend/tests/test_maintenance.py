"""Tests: Maintenance Request API."""

import pytest

RESOURCE_PAYLOAD = {
    "name": "Projector Lab 3",
    "resource_type": "projector",
    "location": "Block C, Room 305",
    "building": "Block C",
    "status": "available",
    "is_active": True,
}

MAINTENANCE_PAYLOAD_TEMPLATE = {
    "reported_by": "Carlos Mendez",
    "reporter_email": "carlos@university.edu",
    "title": "Projector bulb needs replacement",
    "description": "The projector bulb has burned out and the image is very dim.",
    "priority": "high",
}


@pytest.fixture
async def resource_id(client) -> int:
    response = await client.post("/api/resources", json=RESOURCE_PAYLOAD)
    assert response.status_code == 201
    return response.json()["id"]


@pytest.mark.asyncio
async def test_create_maintenance_request(client, resource_id):
    payload = {**MAINTENANCE_PAYLOAD_TEMPLATE, "resource_id": resource_id}
    response = await client.post("/api/maintenance", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "open"
    assert body["priority"] == "high"
    assert body["resource_id"] == resource_id


@pytest.mark.asyncio
async def test_create_maintenance_invalid_priority(client, resource_id):
    payload = {**MAINTENANCE_PAYLOAD_TEMPLATE, "resource_id": resource_id, "priority": "extreme"}
    response = await client.post("/api/maintenance", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_maintenance_not_found(client):
    response = await client.get("/api/maintenance/9999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_maintenance(client, resource_id):
    payload = {**MAINTENANCE_PAYLOAD_TEMPLATE, "resource_id": resource_id}
    await client.post("/api/maintenance", json=payload)

    response = await client.get("/api/maintenance")
    assert response.status_code == 200
    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_update_maintenance_status_to_resolved(client, resource_id):
    payload = {**MAINTENANCE_PAYLOAD_TEMPLATE, "resource_id": resource_id}
    create_resp = await client.post("/api/maintenance", json=payload)
    mr_id = create_resp.json()["id"]

    update_resp = await client.put(
        f"/api/maintenance/{mr_id}",
        json={"status": "resolved", "resolution_notes": "Bulb replaced by facilities team."},
    )
    assert update_resp.status_code == 200
    body = update_resp.json()
    assert body["status"] == "resolved"
    assert body["resolution_notes"] == "Bulb replaced by facilities team."


@pytest.mark.asyncio
async def test_delete_maintenance_request(client, resource_id):
    payload = {**MAINTENANCE_PAYLOAD_TEMPLATE, "resource_id": resource_id}
    create_resp = await client.post("/api/maintenance", json=payload)
    mr_id = create_resp.json()["id"]

    delete_resp = await client.delete(f"/api/maintenance/{mr_id}")
    assert delete_resp.status_code == 204

    get_resp = await client.get(f"/api/maintenance/{mr_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_filter_maintenance_by_priority(client, resource_id):
    await client.post("/api/maintenance", json={**MAINTENANCE_PAYLOAD_TEMPLATE, "resource_id": resource_id, "priority": "critical"})
    await client.post("/api/maintenance", json={**MAINTENANCE_PAYLOAD_TEMPLATE, "resource_id": resource_id, "priority": "low"})

    response = await client.get("/api/maintenance?priority=critical")
    assert response.status_code == 200
    for m in response.json():
        assert m["priority"] == "critical"
