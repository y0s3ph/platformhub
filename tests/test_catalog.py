"""Tests for catalog endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestCatalog:
    async def test_list_catalog(self, client: AsyncClient):
        res = await client.get("/api/catalog/")
        assert res.status_code == 200
        items = res.json()
        assert len(items) == 3
        types = {i["resource_type"] for i in items}
        assert types == {"k8s_namespace", "s3_bucket", "rds_database"}

    async def test_get_catalog_item(self, client: AsyncClient):
        res = await client.get("/api/catalog/k8s_namespace")
        assert res.status_code == 200
        data = res.json()
        assert data["display_name"] == "Kubernetes Namespace"
        assert len(data["parameters"]) > 0

    async def test_get_catalog_item_not_found(self, client: AsyncClient):
        res = await client.get("/api/catalog/nonexistent")
        assert res.status_code == 422
