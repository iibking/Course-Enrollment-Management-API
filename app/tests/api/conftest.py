import pytest
from app.core.db import users, courses, enrollments


# This fixture will run before each test to clear the in-memory database
@pytest.fixture(autouse=True)
def clear_db():
    users.clear()
    courses.clear()
    enrollments.clear()
    yield