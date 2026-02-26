"""Tests for authentication endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAuth:
    async def test_register(self, client: AsyncClient):
        res = await client.post("/api/auth/register", json={
            "username": "newuser",
            "email": "new@test.com",
            "password": "securepass123",
        })
        assert res.status_code == 201
        data = res.json()
        assert data["username"] == "newuser"
        assert data["role"] == "developer"

    async def test_register_duplicate(self, client: AsyncClient):
        payload = {"username": "dup", "email": "dup@test.com", "password": "securepass123"}
        await client.post("/api/auth/register", json=payload)
        res = await client.post("/api/auth/register", json=payload)
        assert res.status_code == 400

    async def test_login_success(self, client: AsyncClient):
        await client.post("/api/auth/register", json={
            "username": "loginuser",
            "email": "login@test.com",
            "password": "securepass123",
        })
        res = await client.post("/api/auth/login", data={
            "username": "loginuser",
            "password": "securepass123",
        })
        assert res.status_code == 200
        assert "access_token" in res.json()

    async def test_login_wrong_password(self, client: AsyncClient):
        await client.post("/api/auth/register", json={
            "username": "wrongpw",
            "email": "wrong@test.com",
            "password": "securepass123",
        })
        res = await client.post("/api/auth/login", data={
            "username": "wrongpw",
            "password": "badpassword",
        })
        assert res.status_code == 401

    async def test_protected_endpoint_no_token(self, client: AsyncClient):
        res = await client.get("/api/requests/")
        assert res.status_code == 401
