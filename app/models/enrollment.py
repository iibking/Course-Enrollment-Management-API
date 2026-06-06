from sqlalchemy import ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import TYPE_CHECKING

from app.core.db_async import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.course import Course


class Enrollment(Base):
    __tablename__ = "enrollments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # Many-to-One back-references
    user: Mapped["User"] = relationship("User", back_populates="enrollments")
    course: Mapped["Course"] = relationship("Course", back_populates="enrollments")

    # A student can enrol in a given course only once (enforced by the DB).
    __table_args__ = (
        UniqueConstraint("user_id", "course_id", name="uq_enrollment_user_course"),
    )