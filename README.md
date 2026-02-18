# 📚 Course Enrollment API

A RESTful API built with **FastAPI** for managing course enrollments. It supports user registration, course management, and enrollment operations with role-based access control for admins and students.

---

## 🗂️ Project Structure

```
app/
├── main.py                  # App entry point
├── api/
│   ├── dependencies.py      # Role-based access control
│   └── v1/
│       ├── users.py         # User routes
│       ├── courses.py       # Course routes
│       └── enrollments.py   # Enrollment routes
├── core/
│   └── db.py                # In-memory database
├── schemas/
│   ├── user_schema.py
│   ├── course_schema.py
│   └── enroll_schema.py
├── services/
│   ├── user.py
│   ├── course.py
│   └── enroll.py
└── tests/
    └── api/                 # API tests
        ├── test_user.py
        ├── test_course.py
        └── test_enroll.py
```

---

## ⚙️ Prerequisites

- Python 3.10+
- pip

---

## 🚀 Getting Started

### 1. Create and activate a virtual environment

```bash
# Create virtual environment
python -m venv venv

# Activate — Windows
venv\Scripts\activate

# Activate — macOS/Linux
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install fastapi uvicorn pydantic
```

---

## ▶️ Running the API

Start the development server from the **project root** 

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```
http://127.0.0.1:8000
```

```
http://localhost:8000
```

### Interactive Docs

FastAPI generates documentation automatically. Once the server is running, visit:

| Interface | URL |
|-----------|-----|
| Swagger UI | http://127.0.0.1:8000/docs |
| ReDoc | http://127.0.0.1:8000/redoc |

---

## 📌 API Overview

### Users — `/users`

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/users/` | Create a new user | None |
| GET | `/users/` | Get all users | None |
| GET | `/users/{user_id}` | Get a user by ID | None |

### Courses — `/courses`

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/courses/?user_id=` | Create a course | Admin |
| PUT | `/courses/{course_id}?user_id=` | Update a course | Admin |
| DELETE | `/courses/{course_id}?user_id=` | Delete a course | Admin |
| GET | `/courses/` | Get all courses | None |
| GET | `/courses/{course_id}` | Get a course by ID | None |

### Enrollments — `/enrollments`

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/enrollments/?user_id=` | Enroll in a course | Student |
| DELETE | `/enrollments/{enroll_id}?user_id=` | Deregister from a course | Student (own only) |
| GET | `/enrollments/users/{user_id}?user_id=` | Get a student's enrollments | Student (own only) |
| GET | `/enrollments/?user_id=` | Get all enrollments | Admin |
| GET | `/enrollments/courses/{course_id}?user_id=` | Get enrollments for a course | Admin |
| DELETE | `/enrollments/force/{enroll_id}?user_id=` | Force remove a student | Admin |

> **Note:** Authentication is handled via the `user_id` query parameter. The API checks the user's role from the in-memory database and returns `403 Forbidden` if the role doesn't match the required permission.

---

## 🧪 Running the Tests

### 1. Install test dependencies

```bash
pip install pytest httpx
```

### 2. Run all tests

From the **project root**, run:

```bash
pytest app/tests/api/ -v
```

### 3. Run tests for a specific module

```bash
# Users only
pytest app/tests/api/test_user.py -v

# Courses only
pytest app/tests/api/test_course.py -v

# Enrollments only
pytest app/tests/api/test_enroll.py -v
```

### 4. Run a specific test class or test

```bash
# Run a specific class
pytest app/tests/api/test_course.py::TestCreateCourse -v

# Run a single test
pytest app/tests/api/test_course.py::TestCreateCourse::test_duplicate_course_code -v
```

---

## 🗒️ Notes

- The database is **in-memory** — all data is lost when the server restarts.
- Tests automatically clear the database before each test case using a pytest `autouse` fixture, so tests are fully isolated from one another.


# ENJOY😁