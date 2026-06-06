import os

# Set required settings BEFORE importing the app (config reads env at import).
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
os.environ.setdefault("ENVIRONMENT", "STAGING")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("DATABASE_URL_ASYNC", "sqlite+aiosqlite:///:memory:")

import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.db_async import Base
import app.models  # noqa: F401  (registers tables on Base.metadata)
from app.core.deps import get_async_db
from app.main import app


# Database (one fresh in-memory DB per test)
@pytest_asyncio.fixture
async def db_engine():
    """A throwaway in-memory async engine; StaticPool keeps one shared connection."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine):
    """Direct DB access for tests that need to set up state (e.g. deactivate a user)."""
    SessionLocal = sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    async with SessionLocal() as session:
        yield session


@pytest_asyncio.fixture(autouse=True)
async def _override_db(db_engine):
    """Point the app's DB dependency at the test engine for the duration of a test."""
    SessionLocal = sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)

    async def _get_test_db():
        async with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_async_db] = _get_test_db
    yield
    app.dependency_overrides.clear()


# HTTP client 
@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# Auth helpers 
async def _register_and_login(client, name, email, password, role=None):
    payload = {"name": name, "email": email, "password": password}
    if role:
        payload["role"] = role
    await client.post("/auth/register", json=payload)
    resp = await client.post("/auth/token", data={"username": email, "password": password})
    return resp.json()["access_token"]


@pytest_asyncio.fixture
async def student_headers(client):
    token = await _register_and_login(client, "Stud", "student@x.com", "supersecret")
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def admin_headers(client):
    token = await _register_and_login(client, "Admin", "admin@x.com", "supersecret", role="admin")
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def course(client, admin_headers):
    """A ready-made active course (capacity 2) created by an admin."""
    resp = await client.post(
        "/courses",
        json={"title": "Intro to CS", "code": "CS101", "capacity": 2},
        headers=admin_headers,
    )
    return resp.json()