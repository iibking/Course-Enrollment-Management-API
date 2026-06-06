from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course
from app.schemas.course_schema import CourseCreate, CourseUpdate


class CourseRepository:
    @staticmethod
    async def get_by_id(db: AsyncSession, course_id: int) -> Course | None:
        result = await db.execute(select(Course).where(Course.id == course_id))
        return result.scalars().first()

    @staticmethod
    async def get_by_code(db: AsyncSession, code: str) -> Course | None:
        """Used for the unique-code check on create/update."""
        result = await db.execute(select(Course).where(Course.code == code))
        return result.scalars().first()

    @staticmethod
    async def get_all(db: AsyncSession, active_only: bool = False) -> list[Course]:
        stmt = select(Course).order_by(Course.id)
        if active_only:
            stmt = stmt.where(Course.is_active.is_(True))
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def create(db: AsyncSession, data: CourseCreate) -> Course:
        course = Course(**data.model_dump())
        db.add(course)
        await db.flush()
        await db.refresh(course)
        return course

    @staticmethod
    async def update(db: AsyncSession, course: Course, data: CourseUpdate) -> Course:
        # Only overwrite fields the client actually sent (partial update).
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(course, key, value)
        await db.flush()
        await db.refresh(course)
        return course

    @staticmethod
    async def delete(db: AsyncSession, course: Course) -> None:
        # cascade="all, delete-orphan" on the relationship removes enrollments too.
        await db.delete(course)
        await db.flush()