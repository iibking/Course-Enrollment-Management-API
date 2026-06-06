from datetime import datetime
from enum import Enum
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# Allowed roles for users
class RoleEnum(str, Enum):
    student = "student"
    admin = "admin"


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    # Role is accepted at registration and defaults to student.
    role: RoleEnum = RoleEnum.student


class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: RoleEnum
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

