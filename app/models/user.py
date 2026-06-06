from sqlalchemy import String, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import TYPE_CHECKING

from app.core.db_async import Base

if TYPE_CHECKING:
    # Imported only for type hints — avoids a circular import at runtime.
    from app.models.enrollment import Enrollment


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))

    # Role drives RBAC. Stored as text; validated against an enum at the schema layer.
    role: Mapped[str] = mapped_column(String(20), default="student")

    # Inactive users cannot authenticate.
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # One-to-Many: a user has many enrollments. Deleting the user removes them.
    enrollments: Mapped[list["Enrollment"]] = relationship(
        "Enrollment",
        back_populates="user",
        cascade="all, delete-orphan",
    )