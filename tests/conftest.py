"""Shared test fixtures."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from platformhub.database import Base, get_db
from platformhub.main import app

TEST_DB_URL = "sqlite+aiosqlite:///file::memory:?cache=shared&uri=true"


@pytest.fixture
async def db_session():
    engine = create_async_engine(TEST_DB_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def client(db_session: AsyncSession):
    async def _override_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def auth_headers(client: AsyncClient) -> dict[str, str]:
    """Register a user and return auth headers."""
    await client.post(
        "/api/auth/register",
        json={
            "username": "testdev",
            "email": "dev@test.com",
            "password": "testpass123",
        },
    )
    res = await client.post(
        "/api/auth/login",
        data={
            "username": "testdev",
            "password": "testpass123",
        },
    )
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def approver_headers(client: AsyncClient, db_session: AsyncSession) -> dict[str, str]:
    """Register an approver user and return auth headers."""
    from platformhub.auth import hash_password
    from platformhub.models import Role, User

    user = User(
        username="testapprover",
        email="approver@test.com",
        hashed_password=hash_password("approverpass123"),
        role=Role.APPROVER,
    )
    db_session.add(user)
    await db_session.commit()

    res = await client.post(
        "/api/auth/login",
        data={
            "username": "testapprover",
            "password": "approverpass123",
        },
    )
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
