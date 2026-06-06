from sqlalchemy import String, Boolean, Integer, CheckConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import TYPE_CHECKING

from app.core.db_async import Base

if TYPE_CHECKING:
    from app.models.enrollment import Enrollment


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200))
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    capacity: Mapped[int] = mapped_column(Integer)

    # Inactive courses are hidden from the public list and reject new enrollments.
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


    # One-to-Many: a course has many enrollments. Deleting the course removes them.
    enrollments: Mapped[list["Enrollment"]] = relationship(
        "Enrollment",
        back_populates="course",
        cascade="all, delete-orphan",
    )

    # DB-level guarantee that capacity is always positive (
    __table_args__ = (
        CheckConstraint("capacity > 0", name="ck_course_capacity_positive"),
    )