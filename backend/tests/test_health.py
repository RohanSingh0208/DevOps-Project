"""Tests: health and readiness endpoints."""

import pytest


@pytest.mark.asyncio
async def test_health_returns_ok(client):
    response = await client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "service" in body
    assert "version" in body


@pytest.mark.asyncio
async def test_root_endpoint(client):
    response = await client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert "Campus Resource Hub" in body["message"]
    assert "/docs" in body["docs"]


@pytest.mark.asyncio
async def test_metrics_endpoint_responds(client):
    """Metrics endpoint must return a 200 with Prometheus text format."""
    response = await client.get("/metrics")
    assert response.status_code == 200
    content = response.text
    # Prometheus format always starts with # HELP or has metric lines
    assert "http_" in content or "process_" in content or "python_" in content
