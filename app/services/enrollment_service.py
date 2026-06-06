from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.enrollment import Enrollment
from app.models.user import User
from app.repositories.course_repository import CourseRepository
from app.repositories.enrollment_repository import EnrollmentRepository


class EnrollmentService:
    @staticmethod
    async def enroll(db: AsyncSession, student: User, course_id: int) -> Enrollment:
        course = await CourseRepository.get_by_id(db, course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
            )
        if not course.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Course is not active",
            )
        if await EnrollmentRepository.get_by_user_and_course(db, student.id, course_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Already enrolled in this course",
            )
        enrolled = await EnrollmentRepository.count_for_course(db, course_id)
        if enrolled >= course.capacity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Course is full"
            )
        return await EnrollmentRepository.create(db, student.id, course_id)

    @staticmethod
    async def deregister(db: AsyncSession, student: User, course_id: int) -> None:
        """A student removes their own enrollment."""
        enrollment = await EnrollmentRepository.get_by_user_and_course(
            db, student.id, course_id
        )
        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="You are not enrolled in this course",
            )
        await EnrollmentRepository.delete(db, enrollment)


    # Admin oversight 
    @staticmethod
    async def list_all(db: AsyncSession) -> list[Enrollment]:
        return await EnrollmentRepository.get_all(db)

    @staticmethod
    async def list_for_course(db: AsyncSession, course_id: int) -> list[Enrollment]:
        course = await CourseRepository.get_by_id(db, course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
            )
        return await EnrollmentRepository.get_for_course(db, course_id)

    @staticmethod
    async def admin_remove(db: AsyncSession, enrollment_id: int) -> None:
        """Admin removes any enrollment by its id."""
        enrollment = await EnrollmentRepository.get_by_id(db, enrollment_id)
        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found"
            )
        await EnrollmentRepository.delete(db, enrollment)
    