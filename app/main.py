from fastapi import FastAPI
from app.api.v1.users import user_router
from app.api.v1.courses import course_router
from app.api.v1.enrollments import enroll_router


app = FastAPI(title="Course Enrollment System")

app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(course_router, prefix="/courses", tags=["Courses"])
app.include_router(enroll_router, prefix="/enrollments", tags=["Enrollments"])
