from pydantic import BaseModel, Field


class CourseBase(BaseModel):
    title: str = Field(..., min_length=1)
    code: str = Field(..., min_length=1)

class CourseCreate(CourseBase):
    pass

class CourseUpdate(CourseBase):
    pass

class Course(CourseBase):
    id: int

