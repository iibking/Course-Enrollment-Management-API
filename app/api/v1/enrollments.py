from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_async_db, require_admin, require_student
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.enroll_schema import EnrollmentRead, EnrollmentAdminRead
from app.services.enrollment_service import EnrollmentService

router = APIRouter(prefix="/enrollments", tags=["Enrollments"])


# Student actions 
@router.post("/{course_id}", response_model=EnrollmentRead, status_code=status.HTTP_201_CREATED)
async def enroll(
    course_id: int,
    db: AsyncSession = Depends(get_async_db),
    student: User = Depends(require_student),
):
    """Student: enrol in a course. Enforces active """
    enrollment = await EnrollmentService.enroll(db, student, course_id)
    await db.commit()
    return enrollment


@router.delete("/{course_id}", response_model=MessageResponse)
async def deregister(
    course_id: int,
    db: AsyncSession = Depends(get_async_db),
    student: User = Depends(require_student),
):
    """Student: deregister yourself from a course (404 if not enrolled)."""
    await EnrollmentService.deregister(db, student, course_id)
    await db.commit()
    return MessageResponse(message="Deregistered successfully")


# Admin oversight 
@router.get("", response_model=list[EnrollmentAdminRead])
async def list_enrollments(
    course_id: Optional[int] = None,
    db: AsyncSession = Depends(get_async_db),
    _admin: User = Depends(require_admin),
):
    """
    Admin: view all enrollments, or only those for a course
    Each row embeds the student and course details.
    """
    if course_id is not None:
        return await EnrollmentService.list_for_course(db, course_id)
    return await EnrollmentService.list_all(db)


@router.delete("/admin/{enrollment_id}", response_model=MessageResponse)
async def admin_remove_enrollment(
    enrollment_id: int,
    db: AsyncSession = Depends(get_async_db),
    _admin: User = Depends(require_admin),
):
    """Admin: remove any enrollment by its id (404 if missing)."""
    await EnrollmentService.admin_remove(db, enrollment_id)
    await db.commit()
    return MessageResponse(message="Enrollment removed successfully")