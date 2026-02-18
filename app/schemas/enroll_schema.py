from pydantic import BaseModel


class EnrollBase(BaseModel):
    user_id: int
    course_id: int

class EnrollCreate(EnrollBase):
    pass

class Enroll(EnrollBase):
    id: int
