"""Tests for resource request endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestRequests:
    async def test_create_request(self, client: AsyncClient, auth_headers: dict):
        res = await client.post("/api/requests/", json={
            "resource_type": "k8s_namespace",
            "name": "my-service",
            "environment": "dev",
            "parameters": {"cpu_limit": "1", "memory_limit": "1Gi", "team": "backend"},
        }, headers=auth_headers)
        assert res.status_code == 201
        data = res.json()
        assert data["name"] == "my-service"
        assert data["status"] == "pending"

    async def test_create_request_invalid_name(self, client: AsyncClient, auth_headers: dict):
        res = await client.post("/api/requests/", json={
            "resource_type": "k8s_namespace",
            "name": "Invalid-Name",
            "environment": "dev",
        }, headers=auth_headers)
        assert res.status_code == 422

    async def test_list_requests(self, client: AsyncClient, auth_headers: dict):
        await client.post("/api/requests/", json={
            "resource_type": "s3_bucket",
            "name": "data-lake",
            "environment": "staging",
        }, headers=auth_headers)
        res = await client.get("/api/requests/", headers=auth_headers)
        assert res.status_code == 200
        assert len(res.json()) >= 1

    async def test_get_request(self, client: AsyncClient, auth_headers: dict):
        create_res = await client.post("/api/requests/", json={
            "resource_type": "rds_database",
            "name": "orders-db",
            "environment": "production",
            "parameters": {"engine_version": "16", "instance_class": "db.t3.small"},
        }, headers=auth_headers)
        req_id = create_res.json()["id"]

        res = await client.get(f"/api/requests/{req_id}", headers=auth_headers)
        assert res.status_code == 200
        assert res.json()["name"] == "orders-db"

    async def test_get_audit_trail(self, client: AsyncClient, auth_headers: dict):
        create_res = await client.post("/api/requests/", json={
            "resource_type": "k8s_namespace",
            "name": "audit-test",
            "environment": "dev",
        }, headers=auth_headers)
        req_id = create_res.json()["id"]

        res = await client.get(f"/api/requests/{req_id}/audit", headers=auth_headers)
        assert res.status_code == 200
        logs = res.json()
        assert len(logs) >= 1
        assert logs[0]["action"] == "created"
