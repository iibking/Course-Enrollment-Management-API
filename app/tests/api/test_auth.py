"""Tests for registration, login, and profile retrieval."""
import pytest
from sqlalchemy import select

from app.models.user import User


# Registration 
async def test_register_student(client):
    r = await client.post("/auth/register", json={
        "name": "Ada", "email": "ada@x.com", "password": "supersecret"})
    assert r.status_code == 201
    body = r.json()
    assert body["role"] == "student"          # defaults to student
    assert body["is_active"] is True
    assert "password" not in body             # never leak the password
    assert "hashed_password" not in body


async def test_register_admin(client):
    r = await client.post("/auth/register", json={
        "name": "Boss", "email": "boss@x.com", "password": "supersecret", "role": "admin"})
    assert r.status_code == 201
    assert r.json()["role"] == "admin"


async def test_register_duplicate_email(client):
    payload = {"name": "Ada", "email": "ada@x.com", "password": "supersecret"}
    await client.post("/auth/register", json=payload)
    r = await client.post("/auth/register", json=payload)
    assert r.status_code == 409


@pytest.mark.parametrize("payload", [
    {"name": "A", "email": "not-an-email", "password": "supersecret"},  # bad email
    {"name": "A", "email": "a@x.com", "password": "short"},             # short pw
    {"name": "A", "email": "a@x.com", "password": "supersecret", "role": "root"},  # bad role
    {"email": "a@x.com", "password": "supersecret"},                    # missing name
])
async def test_register_validation_errors(client, payload):
    r = await client.post("/auth/register", json=payload)
    assert r.status_code == 422


# ── Login ────────────────────────────────────────────────────────
async def test_login_success(client):
    await client.post("/auth/register", json={
        "name": "Ada", "email": "ada@x.com", "password": "supersecret"})
    r = await client.post("/auth/token", data={"username": "ada@x.com", "password": "supersecret"})
    assert r.status_code == 200
    assert r.json()["token_type"] == "bearer"
    assert r.json()["access_token"]


async def test_login_wrong_password(client):
    await client.post("/auth/register", json={
        "name": "Ada", "email": "ada@x.com", "password": "supersecret"})
    r = await client.post("/auth/token", data={"username": "ada@x.com", "password": "WRONG"})
    assert r.status_code == 401


async def test_login_nonexistent_user(client):
    r = await client.post("/auth/token", data={"username": "ghost@x.com", "password": "supersecret"})
    assert r.status_code == 401


async def test_inactive_user_cannot_login(client, db_session):
    """Spec rule: inactive users cannot authenticate."""
    await client.post("/auth/register", json={
        "name": "Ada", "email": "ada@x.com", "password": "supersecret"})
    # Deactivate directly in the DB (no public endpoint deactivates users).
    user = (await db_session.execute(select(User).where(User.email == "ada@x.com"))).scalars().first()
    user.is_active = False
    await db_session.commit()
    r = await client.post("/auth/token", data={"username": "ada@x.com", "password": "supersecret"})
    assert r.status_code == 401


# ── Profile ──────────────────────────────────────────────────────
async def test_me_requires_auth(client):
    r = await client.get("/auth/me")
    assert r.status_code == 401


async def test_me_returns_profile(client, student_headers):
    r = await client.get("/auth/me", headers=student_headers)
    assert r.status_code == 200
    assert r.json()["email"] == "student@x.com"
    assert r.json()["role"] == "student"