from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)



def create_admin():
    res = client.post("/users/", json={"name": "King", "email": "king@gta.com", "role": "admin"})
    return res.json()["id"]

def create_student(name="Rihanna", email="rihanna@student.com"):
    res = client.post("/users/", json={"name": name, "email": email, "role": "student"})
    return res.json()["id"]

def create_course(user_id, title="Mathematics", code="MAT101"):
    res = client.post("/courses/", json={"title": title, "code": code}, params={"user_id": user_id})
    return res.json()["id"]

def enroll(student_id, course_id):
    return client.post(
        "/enrollments/",
        json={"user_id": student_id, "course_id": course_id},
        params={"user_id": student_id}
    )


#Test cases for enrollment creation, deletion, and retrieval
def test_student_can_enroll_in_course():
    admin_id = create_admin()
    student_id = create_student()
    course_id = create_course(admin_id)
    res = enroll(student_id, course_id)
    assert res.status_code == 201
    assert res.json()["user_id"] == student_id
    assert res.json()["course_id"] == course_id

def test_admin_cannot_enroll():
    admin_id = create_admin()
    course_id = create_course(admin_id)
    res = client.post("/enrollments/", json={"user_id": admin_id, "course_id": course_id}, params={"user_id": admin_id})
    assert res.status_code == 403

def test_enroll_in_nonexistent_course():
    student_id = create_student()
    res = client.post("/enrollments/", json={"user_id": student_id, "course_id": 69}, params={"user_id": student_id})
    assert res.status_code == 404

def test_duplicate_enrollment():
    admin_id = create_admin()
    student_id = create_student()
    course_id = create_course(admin_id)
    enroll(student_id, course_id)
    res = enroll(student_id, course_id)
    assert res.status_code == 409



def test_student_can_deregister_own_enrollment():
    admin_id = create_admin()
    student_id = create_student()
    course_id = create_course(admin_id)
    enroll_id = enroll(student_id, course_id).json()["id"]
    res = client.delete(f"/enrollments/{enroll_id}", params={"user_id": student_id})
    assert res.status_code == 200


def test_deregister_nonexistent_enrollment():
    student_id = create_student()
    res = client.delete("/enrollments/69", params={"user_id": student_id})
    assert res.status_code == 404



def test_student_can_view_own_enrollments():
    admin_id = create_admin()
    student_id = create_student()
    course_id = create_course(admin_id)
    enroll(student_id, course_id)
    res = client.get(f"/enrollments/users/{student_id}", params={"user_id": student_id})
    assert res.status_code == 200
    assert len(res.json()) == 1



def test_admin_can_get_all_enrollments():
    admin_id = create_admin()
    student_id = create_student()
    course_id = create_course(admin_id)
    enroll(student_id, course_id)
    res = client.get("/enrollments/", params={"user_id": admin_id})
    assert res.status_code == 200
    assert len(res.json()) == 1

def test_student_cannot_get_all_enrollments():
    student_id = create_student()
    res = client.get("/enrollments/", params={"user_id": student_id})
    assert res.status_code == 403



def test_admin_can_get_enrollments_by_course():
    admin_id = create_admin()
    student_id = create_student()
    course_id = create_course(admin_id)
    enroll(student_id, course_id)
    res = client.get(f"/enrollments/courses/{course_id}", params={"user_id": admin_id})
    assert res.status_code == 200
    assert all(e["course_id"] == course_id for e in res.json())

def test_get_enrollments_for_nonexistent_course():
    admin_id = create_admin()
    res = client.get("/enrollments/courses/999", params={"user_id": admin_id})
    assert res.status_code == 404



def test_admin_can_force_deregister_a_student():
    admin_id = create_admin()
    student_id = create_student()
    course_id = create_course(admin_id)
    enroll_id = enroll(student_id, course_id).json()["id"]
    res = client.delete(f"/enrollments/force/{enroll_id}", params={"user_id": admin_id})
    assert res.status_code == 200

def test_student_cannot_force_deregister():
    admin_id = create_admin()
    student_id = create_student()
    course_id = create_course(admin_id)
    enroll_id = enroll(student_id, course_id).json()["id"]
    res = client.delete(f"/enrollments/force/{enroll_id}", params={"user_id": student_id})
    assert res.status_code == 403

def test_force_deregister_nonexistent_enrollment():
    admin_id = create_admin()
    res = client.delete("/enrollments/force/69", params={"user_id": admin_id})
    assert res.status_code == 404