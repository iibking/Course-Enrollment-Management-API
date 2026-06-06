from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.course import Course
from app.repositories.course_repository import CourseRepository
from app.schemas.course_schema import CourseCreate, CourseUpdate


class CourseService:
    @staticmethod
    async def list_active(db: AsyncSession) -> list[Course]:
        """Public listing — active courses only."""
        return await CourseRepository.get_all(db, active_only=True)

    @staticmethod
    async def get(db: AsyncSession, course_id: int) -> Course:
        course = await CourseRepository.get_by_id(db, course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
            )
        return course

    @staticmethod
    async def create(db: AsyncSession, data: CourseCreate) -> Course:
        if await CourseRepository.get_by_code(db, data.code):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Course code already exists",
            )
        return await CourseRepository.create(db, data)

    @staticmethod
    async def update(db: AsyncSession, course_id: int, data: CourseUpdate) -> Course:
        course = await CourseService.get(db, course_id)   # 404 if missing
        # If the code is being changed, make sure the new one isn't taken.
        if data.code and data.code != course.code:
            if await CourseRepository.get_by_code(db, data.code):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Course code already exists",
                )
        return await CourseRepository.update(db, course, data)

    @staticmethod
    async def delete(db: AsyncSession, course_id: int) -> None:
        course = await CourseService.get(db, course_id)   # 404 if missing
        await CourseRepository.delete(db, course)