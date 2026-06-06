from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_async_db, require_admin
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.course_schema import CourseCreate, CourseUpdate, CourseRead
from app.services.course_service import CourseService

router = APIRouter(prefix="/courses", tags=["Courses"])


# Public reads 
@router.get("", response_model=list[CourseRead])
async def list_courses(db: AsyncSession = Depends(get_async_db)):
    """Public: list all active courses."""
    return await CourseService.list_active(db)


@router.get("/{course_id}", response_model=CourseRead)
async def get_course(course_id: int, db: AsyncSession = Depends(get_async_db)):
    """Public: retrieve a single course by id (404 if missing)."""
    return await CourseService.get(db, course_id)


# Admin-only writes 
@router.post("", response_model=CourseRead, status_code=status.HTTP_201_CREATED)
async def create_course(
    data: CourseCreate,
    db: AsyncSession = Depends(get_async_db),
    _admin: User = Depends(require_admin),
):
    """Admin: create a course. Code must be unique (409)."""
    course = await CourseService.create(db, data)
    await db.commit()
    return course


@router.patch("/{course_id}", response_model=CourseRead)
async def update_course(
    course_id: int,
    data: CourseUpdate,
    db: AsyncSession = Depends(get_async_db),
    _admin: User = Depends(require_admin),
):
    """Admin: update course details, including is_active to (de)activate it."""
    course = await CourseService.update(db, course_id, data)
    await db.commit()
    return course


@router.delete("/{course_id}", response_model=MessageResponse)
async def delete_course(
    course_id: int,
    db: AsyncSession = Depends(get_async_db),
    _admin: User = Depends(require_admin),
):
    """Admin: delete a course (and its enrollments via cascade)."""
    await CourseService.delete(db, course_id)
    await db.commit()
    return MessageResponse(message="Course deleted successfully")