from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)



def create_admin():
    res = client.post("/users/", json={"name": "Ibro", "email": "ibro@email.com", "role": "admin"})
    return res.json()["id"]

def create_student():
    res = client.post("/users/", json={"name": "Tyla", "email": "tyla@student.com", "role": "student"})
    return res.json()["id"]

def create_course(user_id, title="Mathematics", code="MAT101"):
    return client.post("/courses/", json={"title": title, "code": code}, params={"user_id": user_id})



#Test cases for course creation, update, deletion, and retrieval
def test_admin_can_create_course():
    admin_id = create_admin()
    res = create_course(admin_id)
    assert res.status_code == 201
    data = res.json()
    assert data["title"] == "Mathematics"
    assert data["code"] == "MAT101"

def test_student_cannot_create_course():
    student_id = create_student()
    res = create_course(student_id)
    assert res.status_code == 403

def test_duplicate_course_code():
    admin_id = create_admin()
    create_course(admin_id, title="Mathematics", code="MAT101")
    res = create_course(admin_id, title="Math Advanced", code="MAT101")
    assert res.status_code == 409



def test_admin_can_update_course():
    admin_id = create_admin()
    create_course(admin_id)
    res = client.put("/courses/1", json={"title": "Futhermaths", "code": "MAT202"}, params={"user_id": admin_id})
    assert res.status_code == 200
    assert res.json()["title"] == "Futhermaths"

def test_update_nonexistent_course():
    admin_id = create_admin()
    res = client.put("/courses/69", json={"title": "Chemistry", "code": "CHM101"}, params={"user_id": admin_id})
    assert res.status_code == 404

def test_update_course_with_duplicate_code():
    admin_id = create_admin()
    create_course(admin_id, title="Mathematics", code="MAT101")
    create_course(admin_id, title="Physics", code="PHY101")
    res = client.put("/courses/2", json={"title": "Physics", "code": "MAT101"}, params={"user_id": admin_id})
    assert res.status_code == 409

def test_student_cannot_update_course():
    admin_id = create_admin()
    student_id = create_student()
    create_course(admin_id)
    res = client.put("/courses/1", json={"title": "Chemistry", "code": "CHM101"}, params={"user_id": student_id})
    assert res.status_code == 403



def test_admin_can_delete_course():
    admin_id = create_admin()
    create_course(admin_id)
    res = client.delete("/courses/1", params={"user_id": admin_id})
    assert res.status_code == 200

def test_delete_nonexistent_course():
    admin_id = create_admin()
    res = client.delete("/courses/69", params={"user_id": admin_id})
    assert res.status_code == 404

def test_student_cannot_delete_course():
    admin_id = create_admin()
    student_id = create_student()
    create_course(admin_id)
    res = client.delete("/courses/1", params={"user_id": student_id})
    assert res.status_code == 403



def test_get_all_courses_is_public():
    res = client.get("/courses/")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_get_course_by_id_returns_correct_course():
    admin_id = create_admin()
    create_course(admin_id, title="Math 101", code="MTH101")
    res = client.get("/courses/1")
    assert res.status_code == 200
    assert res.json()["code"] == "MTH101"

def test_get_nonexistent_course():
    res = client.get("/courses/666")
    assert res.status_code == 404
    assert res.json()["detail"] == "Course not found"