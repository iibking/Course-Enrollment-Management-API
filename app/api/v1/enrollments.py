from fastapi import APIRouter,Depends, HTTPException, status
from app.schemas.enroll_schema import EnrollCreate, Enroll
from app.services.enroll import EnrollService
from app.api.dependencies import is_student_user, is_admin_user
from app.schemas.user_schema import User
from app.services.course import CourseService
from typing import List


enroll_router = APIRouter()

#Enrolling for a course (Student only)
@enroll_router.post("/", response_model=Enroll, status_code=status.HTTP_201_CREATED)
def create_enrollment(enroll_in: EnrollCreate, current_user: User = Depends(is_student_user)):
    if enroll_in.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only students can enroll")
    return EnrollService.enroll_create(enroll_in)


#Forcefully deregister a student from a course (Admin only)
@enroll_router.delete("/force/{enroll_id}", status_code=status.HTTP_200_OK)
def force_deregister_course(enroll_id: int, current_user: User = Depends(is_admin_user)):
    enrollment = EnrollService.get_enrollments_by_id(enroll_id)
    if not enrollment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")
    return EnrollService.delete_enrollment(enroll_id)


#Deregistering from a course (Student only)
@enroll_router.delete("/{enroll_id}", status_code=status.HTTP_200_OK)
def deregister_course(enroll_id: int, current_user: User = Depends(is_student_user)):
    enrollment = EnrollService.get_enrollments_by_id(enroll_id)
    if not enrollment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")
    if enrollment.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only students can deregister")
    return EnrollService.delete_enrollment(enroll_id)


#Enrollment retrieval for a particular student
@enroll_router.get("/users/{user_id}", response_model=List[Enroll])
def get_enrollments_by_user(user_id: int, current_user: User = Depends(is_student_user)):
    if user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Students can only view their own enrollments")
    return EnrollService.get_enrollments_by_user(user_id)


#Enrollments retrieval (Admin only)
@enroll_router.get("/", response_model=List[Enroll])
def get_enrollments(current_user: User = Depends(is_admin_user)):
    return EnrollService.get_enrollments()


#Enrollments retrieval for a particular course (Admin only)
@enroll_router.get("/courses/{course_id}", response_model=List[Enroll])
def get_enrollments_by_course(course_id: int, current_user: User = Depends(is_admin_user)):
    course = CourseService.get_courses_by_id(course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return EnrollService.get_enrollment_by_course(course_id)