"""Tests for the approval workflow and manifest generation."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestWorkflow:
    async def _create_request(self, client, auth_headers):
        res = await client.post(
            "/api/requests/",
            json={
                "resource_type": "k8s_namespace",
                "name": "team-api",
                "environment": "staging",
                "parameters": {"cpu_limit": "2", "memory_limit": "2Gi", "team": "platform"},
            },
            headers=auth_headers,
        )
        return res.json()["id"]

    async def test_approve_generates_manifest(
        self, client: AsyncClient, auth_headers: dict, approver_headers: dict
    ):
        req_id = await self._create_request(client, auth_headers)

        res = await client.post(
            f"/api/admin/{req_id}/review",
            json={
                "action": "approved",
                "comment": "LGTM",
            },
            headers=approver_headers,
        )
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "approved"
        assert data["generated_manifest"] is not None
        assert "team-api-staging" in data["generated_manifest"]
        assert "ResourceQuota" in data["generated_manifest"]

    async def test_reject_request(
        self, client: AsyncClient, auth_headers: dict, approver_headers: dict
    ):
        req_id = await self._create_request(client, auth_headers)

        res = await client.post(
            f"/api/admin/{req_id}/review",
            json={
                "action": "rejected",
                "comment": "Wrong environment",
            },
            headers=approver_headers,
        )
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "rejected"
        assert data["generated_manifest"] is None

    async def test_double_review_fails(
        self, client: AsyncClient, auth_headers: dict, approver_headers: dict
    ):
        req_id = await self._create_request(client, auth_headers)

        await client.post(
            f"/api/admin/{req_id}/review",
            json={
                "action": "approved",
                "comment": "",
            },
            headers=approver_headers,
        )

        res = await client.post(
            f"/api/admin/{req_id}/review",
            json={
                "action": "rejected",
                "comment": "",
            },
            headers=approver_headers,
        )
        assert res.status_code == 400

    async def test_developer_cannot_review(self, client: AsyncClient, auth_headers: dict):
        req_id = await self._create_request(client, auth_headers)

        res = await client.post(
            f"/api/admin/{req_id}/review",
            json={
                "action": "approved",
                "comment": "",
            },
            headers=auth_headers,
        )
        assert res.status_code == 403

    async def test_pending_list_for_approver(
        self, client: AsyncClient, auth_headers: dict, approver_headers: dict
    ):
        await self._create_request(client, auth_headers)

        res = await client.get("/api/admin/pending", headers=approver_headers)
        assert res.status_code == 200
        assert len(res.json()) >= 1


@pytest.mark.asyncio
class TestManifestGeneration:
    async def test_s3_manifest(
        self, client: AsyncClient, auth_headers: dict, approver_headers: dict
    ):
        res = await client.post(
            "/api/requests/",
            json={
                "resource_type": "s3_bucket",
                "name": "app-assets",
                "environment": "production",
                "parameters": {"versioning": "true", "region": "eu-west-1"},
            },
            headers=auth_headers,
        )
        req_id = res.json()["id"]

        res = await client.post(
            f"/api/admin/{req_id}/review",
            json={
                "action": "approved",
                "comment": "",
            },
            headers=approver_headers,
        )
        manifest = res.json()["generated_manifest"]
        assert "aws_s3_bucket" in manifest
        assert "app-assets-production" in manifest
        assert "block_public_acls" in manifest

    async def test_rds_manifest(
        self, client: AsyncClient, auth_headers: dict, approver_headers: dict
    ):
        res = await client.post(
            "/api/requests/",
            json={
                "resource_type": "rds_database",
                "name": "orders-db",
                "environment": "dev",
                "parameters": {
                    "engine_version": "16",
                    "instance_class": "db.t3.micro",
                    "storage_gb": "20",
                },
            },
            headers=auth_headers,
        )
        req_id = res.json()["id"]

        res = await client.post(
            f"/api/admin/{req_id}/review",
            json={
                "action": "approved",
                "comment": "",
            },
            headers=approver_headers,
        )
        manifest = res.json()["generated_manifest"]
        assert "aws_db_instance" in manifest
        assert "orders-db-dev" in manifest
        assert "storage_encrypted" in manifest
