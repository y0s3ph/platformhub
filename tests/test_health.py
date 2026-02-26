"""Tests for health and page endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestHealth:
    async def test_health_check(self, client: AsyncClient):
        res = await client.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "ok"
        assert "version" in data

    async def test_index_page(self, client: AsyncClient):
        res = await client.get("/")
        assert res.status_code == 200
        assert "PlatformHub" in res.text

    async def test_login_page(self, client: AsyncClient):
        res = await client.get("/login")
        assert res.status_code == 200
        assert "Sign in" in res.text

    async def test_catalog_page(self, client: AsyncClient):
        res = await client.get("/catalog")
        assert res.status_code == 200
        assert "Catalog" in res.text
