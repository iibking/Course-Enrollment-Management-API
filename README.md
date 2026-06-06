# 📚 Course Enrollment Management API

A secure, database-backed REST API for managing a course enrollment platform,
built with FastAPI, SQLAlchemy (async), PostgreSQL, JWT authentication, and
role-based access control.

## Features
- JWT authentication (register / login) with bcrypt-hashed passwords
- Role-based access control (RBAC): `student` and `admin`
- Course management with capacity and active/inactive state
- Enrollment with business rules: unique per student, capacity-aware, active-only
- Admin oversight of all enrollments
- Alembic migrations and a full automated test suite (42 tests)

## Tech stack
FastAPI · SQLAlchemy 2.0 (async, asyncpg) · PostgreSQL · Alembic ·
Pydantic v2 · python-jose (JWT) · bcrypt · pytest

## Architecture
Layered separation of concerns:

    API router  ->  Service (business rules)  ->  Repository (DB access)  ->  Model

## Project structure
    Course-Enrollment-System/
    ├── .env.example              # template for environment variables
    ├── .gitignore
    ├── .dockerignore
    ├── Dockerfile                # container image (used by Render)
    ├── render.yaml               # Render Blueprint (web service + Postgres)
    ├── alembic.ini               # Alembic configuration
    ├── pytest.ini                # pytest configuration
    ├── requirements.txt
    ├── README.md
    ├── alembic/
    │   ├── env.py                # migration environment (points at Base.metadata)
    │   ├── script.py.mako
    │   └── versions/             # migration files
    └── app/
        ├── main.py               # FastAPI app + router registration
        ├── core/
        │   ├── config.py         # settings (env-driven)
        │   ├── db_async.py       # async engine + Base (used by the app)
        │   ├── db.py             # sync engine (used by Alembic)
        │   ├── security.py       # password hashing + JWT
        │   └── deps.py           # DB session + auth/RBAC dependencies
        ├── models/               # SQLAlchemy ORM models
        │   ├── user.py
        │   ├── course.py
        │   └── enrollment.py
        ├── schemas/              # Pydantic request/response models
        │   ├── auth_schema.py
        │   ├── user_schema.py
        │   ├── course_schema.py
        │   ├── enroll_schema.py
        │   └── common.py
        ├── repositories/         # database access
        │   ├── user_repository.py
        │   ├── course_repository.py
        │   └── enrollment_repository.py
        ├── services/             # business logic
        │   ├── auth_service.py
        │   ├── course_service.py
        │   └── enrollment_service.py
        ├── api/v1/               # HTTP routes
        │   ├── auth.py
        │   ├── courses.py
        │   └── enrollments.py
        └── tests/                # pytest suite
            └── api/
                ├── conftest.py
                ├── test_auth.py
                ├── test_courses.py
                └── test_enrollments.py

## Roles & permissions
| Action                       | Student | Admin |
|------------------------------|:-------:|:-----:|
| View courses                 |   ✅    |  ✅   |
| Enroll in a course           |   ✅    |  ❌   |
| Deregister from a course     |   ✅    |  ❌   |
| Create / update / delete course | ❌  |  ✅   |
| View all enrollments         |   ❌    |  ✅   |

## API endpoints
| Method | Path                          | Access  | Description                  |
|--------|-------------------------------|---------|------------------------------|
| POST   | /auth/register                | public  | Register (defaults to student) |
| POST   | /auth/token                   | public  | Log in, returns JWT          |
| GET    | /auth/me                      | auth    | Current user's profile       |
| GET    | /courses                      | public  | List active courses          |
| GET    | /courses/{id}                 | public  | Get a course                 |
| POST   | /courses                      | admin   | Create a course              |
| PATCH  | /courses/{id}                 | admin   | Update / (de)activate course |
| DELETE | /courses/{id}                 | admin   | Delete a course              |
| POST   | /enrollments/{course_id}      | student | Enroll in a course           |
| DELETE | /enrollments/{course_id}      | student | Deregister from a course     |
| GET    | /enrollments[?course_id=]     | admin   | View all / per-course        |
| DELETE | /enrollments/admin/{id}       | admin   | Remove any enrollment        |

## Local setup
1. Create a PostgreSQL database:

       createdb course_enrollment

2. Create your environment file from the template and fill it in:

       cp .env.example .env

   Generate a real secret key and paste it as SECRET_KEY:

       python -c "import secrets; print(secrets.token_hex(32))"

   Both DATABASE_URL and DATABASE_URL_ASYNC must point at the same database,
   differing only in the driver (postgresql:// vs postgresql+asyncpg://).

3. Create and activate a virtual environment, then install dependencies:

       python -m venv venv
       venv\Scripts\activate          # Windows
       # source venv/bin/activate     # macOS/Linux
       pip install -r requirements.txt

## Running migrations
Alembic manages the schema. To apply the existing migration:

    alembic upgrade head

To create a new migration after changing a model (use double quotes on Windows):

    alembic revision --autogenerate -m "describe your change"
    alembic upgrade head

Check the current revision:

    alembic current

## Running the app
    uvicorn app.main:app --reload

Interactive API docs: http://127.0.0.1:8000/docs

## Running tests
The suite uses an isolated in-memory database, so no PostgreSQL is required and
your real data is never touched:

    pytest

All 42 tests should pass.



# LFG😁🚀🚀