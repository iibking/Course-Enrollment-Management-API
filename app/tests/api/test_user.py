from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)



def create_user(name="Doja", email="doja@student.com", role="student"):
    return client.post("/users/", json={"name": name, "email": email, "role": role})


#Test cases for user creation, retrieval, and retrieval by ID
def test_create_user_returns_correct_data():
    res = create_user(name="Doja", email="doja@student.com", role="student")
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "Doja"
    assert data["email"] == "doja@student.com"
    assert data["role"] == "student"
    assert data["id"] == 1

def test_create_user_invalid_email():
    res = client.post("/users/", json={"name": "Doja", "email": "Doja Cat", "role": "student"})
    assert res.status_code == 422

def test_create_user_invalid_role():
    res = client.post("/users/", json={"name": "Doja", "email": "doja@student.com", "role": "superstar"})
    assert res.status_code == 422



def test_get_users_returns_all_created_users():
    create_user(name="Doja", email="doja@student.com", role="student")
    create_user(name="Drake", email="drake@admin.com", role="admin")
    res = client.get("/users/")
    assert res.status_code == 200
    assert len(res.json()) == 2



def test_get_user_by_id_returns_correct_user():
    create_user(name="Doja", email="doja@student.com", role="student")
    res = client.get("/users/1")
    assert res.status_code == 200
    assert res.json()["name"] == "Doja"

def test_get_nonexistent_user():
    res = client.get("/users/69")
    assert res.status_code == 404
    assert res.json()["detail"] == "User not found"