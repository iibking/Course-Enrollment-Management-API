from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas.user_schema import UserRead
from app.schemas.course_schema import CourseRead


# Flat enrollment representation (returned to the enrolling student)
class EnrollmentRead(BaseModel):
    id: int
    user_id: int
    course_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Admin oversight (embeds the student and course)
class EnrollmentAdminRead(EnrollmentRead):
    user: UserRead
    course: CourseRead

    model_config = ConfigDict(from_attributes=True)