from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.enrollment import Enrollment


class EnrollmentRepository:
    @staticmethod
    async def get_by_id(db: AsyncSession, enrollment_id: int) -> Enrollment | None:
        result = await db.execute(
            select(Enrollment).where(Enrollment.id == enrollment_id)
        )
        return result.scalars().first()

    @staticmethod
    async def get_by_user_and_course(
        db: AsyncSession, user_id: int, course_id: int
    ) -> Enrollment | None:
        """Backs the 'cannot enrol twice' rule."""
        result = await db.execute(
            select(Enrollment).where(
                Enrollment.user_id == user_id,
                Enrollment.course_id == course_id,
            )
        )
        return result.scalars().first()

    @staticmethod
    async def count_for_course(db: AsyncSession, course_id: int) -> int:
        """Number of students enrolled — compared against capacity ('course full')."""
        result = await db.execute(
            select(func.count(Enrollment.id)).where(
                Enrollment.course_id == course_id
            )
        )
        return result.scalar_one()

    @staticmethod
    async def create(db: AsyncSession, user_id: int, course_id: int) -> Enrollment:
        enrollment = Enrollment(user_id=user_id, course_id=course_id)
        db.add(enrollment)
        await db.flush()
        await db.refresh(enrollment)
        return enrollment

    @staticmethod
    async def delete(db: AsyncSession, enrollment: Enrollment) -> None:
        await db.delete(enrollment)
        await db.flush()

    # Admin oversight queries (eager-load user + course for serialization)
    @staticmethod
    async def get_all(db: AsyncSession) -> list[Enrollment]:
        result = await db.execute(
            select(Enrollment)
            .options(selectinload(Enrollment.user), selectinload(Enrollment.course))
            .order_by(Enrollment.id)
        )
        return result.scalars().all()

    @staticmethod
    async def get_for_course(db: AsyncSession, course_id: int) -> list[Enrollment]:
        result = await db.execute(
            select(Enrollment)
            .where(Enrollment.course_id == course_id)
            .options(selectinload(Enrollment.user), selectinload(Enrollment.course))
            .order_by(Enrollment.id)
        )
        return result.scalars().all()