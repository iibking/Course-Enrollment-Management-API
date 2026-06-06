from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


# Request body to create a course (admin only)
class CourseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    code: str = Field(min_length=1, max_length=50)
    capacity: int = Field(gt=0, description="Must be greater than zero")
    is_active: bool = True


# Partial update (admin only)
class CourseUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    code: Optional[str] = Field(default=None, min_length=1, max_length=50)
    capacity: Optional[int] = Field(default=None, gt=0)
    is_active: Optional[bool] = None


# Public course representation
class CourseRead(BaseModel):
    id: int
    title: str
    code: str
    capacity: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
