"""Tests for course CRUD, public reads, and admin-only RBAC."""


# Public reads 
async def test_list_courses_public_empty(client):
    r = await client.get("/courses")
    assert r.status_code == 200
    assert r.json() == []


async def test_list_courses_public_after_create(client, course):
    r = await client.get("/courses")            # no auth needed
    assert r.status_code == 200
    assert len(r.json()) == 1
    assert r.json()[0]["code"] == "CS101"


async def test_get_course_public(client, course):
    r = await client.get(f"/courses/{course['id']}")
    assert r.status_code == 200
    assert r.json()["title"] == "Intro to CS"


async def test_get_missing_course(client):
    r = await client.get("/courses/999")
    assert r.status_code == 404


# Create (admin only)
async def test_create_course_requires_auth(client):
    r = await client.post("/courses", json={"title": "X", "code": "X1", "capacity": 5})
    assert r.status_code == 401


async def test_create_course_forbidden_for_student(client, student_headers):
    r = await client.post("/courses", json={"title": "X", "code": "X1", "capacity": 5},
                          headers=student_headers)
    assert r.status_code == 403


async def test_create_course_admin(client, admin_headers):
    r = await client.post("/courses", json={"title": "Math", "code": "MTH101", "capacity": 30},
                          headers=admin_headers)
    assert r.status_code == 201
    assert r.json()["code"] == "MTH101"


async def test_create_duplicate_code(client, admin_headers, course):
    r = await client.post("/courses", json={"title": "Other", "code": "CS101", "capacity": 10},
                          headers=admin_headers)
    assert r.status_code == 409


async def test_create_capacity_zero_rejected(client, admin_headers):
    r = await client.post("/courses", json={"title": "X", "code": "X1", "capacity": 0},
                          headers=admin_headers)
    assert r.status_code == 422


# Update / (de)activate (admin only) 
async def test_update_course_admin(client, admin_headers, course):
    r = await client.patch(f"/courses/{course['id']}", json={"capacity": 50},
                           headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["capacity"] == 50
    assert r.json()["title"] == "Intro to CS"   # unchanged


async def test_update_course_forbidden_for_student(client, student_headers, course):
    r = await client.patch(f"/courses/{course['id']}", json={"capacity": 50},
                           headers=student_headers)
    assert r.status_code == 403


async def test_deactivate_hides_from_public_list(client, admin_headers, course):
    await client.patch(f"/courses/{course['id']}", json={"is_active": False}, headers=admin_headers)
    r = await client.get("/courses")
    assert r.json() == []                       # inactive course not listed publicly


# Delete (admin only) 
async def test_delete_course_admin(client, admin_headers, course):
    r = await client.delete(f"/courses/{course['id']}", headers=admin_headers)
    assert r.status_code == 200
    assert "message" in r.json()
    assert (await client.get(f"/courses/{course['id']}")).status_code == 404


async def test_delete_course_forbidden_for_student(client, student_headers, course):
    r = await client.delete(f"/courses/{course['id']}", headers=student_headers)
    assert r.status_code == 403