"""Tests for enrollment, deregistration, business rules, and admin oversight."""
import pytest_asyncio


@pytest_asyncio.fixture
async def second_student_headers(client):
    """A second student, for capacity/full tests."""
    await client.post("/auth/register", json={
        "name": "Bob", "email": "bob@x.com", "password": "supersecret"})
    tok = (await client.post("/auth/token",
           data={"username": "bob@x.com", "password": "supersecret"})).json()["access_token"]
    return {"Authorization": f"Bearer {tok}"}


# Enroll (student only) 
async def test_enroll_requires_auth(client, course):
    r = await client.post(f"/enrollments/{course['id']}")
    assert r.status_code == 401


async def test_admin_cannot_enroll(client, admin_headers, course):
    r = await client.post(f"/enrollments/{course['id']}", headers=admin_headers)
    assert r.status_code == 403


async def test_student_enroll(client, student_headers, course):
    r = await client.post(f"/enrollments/{course['id']}", headers=student_headers)
    assert r.status_code == 201
    assert r.json()["course_id"] == course["id"]


async def test_enroll_missing_course(client, student_headers):
    r = await client.post("/enrollments/999", headers=student_headers)
    assert r.status_code == 404


async def test_double_enroll_rejected(client, student_headers, course):
    await client.post(f"/enrollments/{course['id']}", headers=student_headers)
    r = await client.post(f"/enrollments/{course['id']}", headers=student_headers)
    assert r.status_code == 409


async def test_course_full(client, admin_headers, student_headers, second_student_headers):
    # capacity 1 course
    cid = (await client.post("/courses", json={"title": "Tiny", "code": "TNY1", "capacity": 1},
           headers=admin_headers)).json()["id"]
    assert (await client.post(f"/enrollments/{cid}", headers=student_headers)).status_code == 201
    r = await client.post(f"/enrollments/{cid}", headers=second_student_headers)
    assert r.status_code == 400          # course full


async def test_enroll_inactive_course(client, admin_headers, student_headers, course):
    await client.patch(f"/courses/{course['id']}", json={"is_active": False}, headers=admin_headers)
    r = await client.post(f"/enrollments/{course['id']}", headers=student_headers)
    assert r.status_code == 400          # course not active


# Deregister (student)
async def test_deregister(client, student_headers, course):
    await client.post(f"/enrollments/{course['id']}", headers=student_headers)
    r = await client.delete(f"/enrollments/{course['id']}", headers=student_headers)
    assert r.status_code == 200
    assert "message" in r.json()


async def test_deregister_not_enrolled(client, student_headers, course):
    r = await client.delete(f"/enrollments/{course['id']}", headers=student_headers)
    assert r.status_code == 404


# Admin oversight 
async def test_admin_view_all_enrollments(client, admin_headers, student_headers, course):
    await client.post(f"/enrollments/{course['id']}", headers=student_headers)
    r = await client.get("/enrollments", headers=admin_headers)
    assert r.status_code == 200
    assert len(r.json()) == 1
    # admin view embeds the student + course
    assert r.json()[0]["user"]["email"] == "student@x.com"
    assert r.json()[0]["course"]["code"] == "CS101"


async def test_student_cannot_view_all_enrollments(client, student_headers, course):
    r = await client.get("/enrollments", headers=student_headers)
    assert r.status_code == 403


async def test_admin_view_enrollments_per_course(client, admin_headers, student_headers, course):
    await client.post(f"/enrollments/{course['id']}", headers=student_headers)
    r = await client.get(f"/enrollments?course_id={course['id']}", headers=admin_headers)
    assert r.status_code == 200
    assert len(r.json()) == 1


async def test_admin_remove_enrollment(client, admin_headers, student_headers, course):
    enr_id = (await client.post(f"/enrollments/{course['id']}", headers=student_headers)).json()["id"]
    r = await client.delete(f"/enrollments/admin/{enr_id}", headers=admin_headers)
    assert r.status_code == 200
    assert "message" in r.json()
    # gone now
    assert (await client.get("/enrollments", headers=admin_headers)).json() == []


async def test_admin_remove_missing_enrollment(client, admin_headers):
    r = await client.delete("/enrollments/admin/999", headers=admin_headers)
    assert r.status_code == 404


async def test_student_cannot_admin_remove(client, student_headers, course):
    r = await client.delete("/enrollments/admin/1", headers=student_headers)
    assert r.status_code == 403