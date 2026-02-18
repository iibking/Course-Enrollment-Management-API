from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.course_schema import Course, CourseCreate, CourseUpdate
from app.services.course import CourseService
from app.api.dependencies import is_admin_user, is_student_user
from app.schemas.user_schema import User
from typing import List

course_router = APIRouter()

##Course manipulation (Admin only)
#Course creation 
@course_router.post("/", response_model=Course, status_code=status.HTTP_201_CREATED)
def create_course(course_in: CourseCreate, current_user: User = Depends(is_admin_user)):
    return CourseService.create_course(course_in)

#Course update
@course_router.put("/{course_id}", response_model=Course, status_code=status.HTTP_200_OK)
def update_course(course_id: int, course_in: CourseUpdate, current_user: User = Depends(is_admin_user)):
    return CourseService.update_course(course_id, course_in)

#Course deletion
@course_router.delete("/{course_id}", status_code=status.HTTP_200_OK)
def delete_course(course_id: int, current_user: User = Depends(is_admin_user)):
    CourseService.delete_course(course_id)
    return {"Message": "Course deleted successfully"} 


##Course retrieval (Public)
# To retrieve all courses  
@course_router.get("/", response_model=List[Course])
def get_courses():
    return CourseService.get_courses()

#To retrieve a course by ID
@course_router.get("/{course_id}", response_model=Course)
def get_course_by_id(course_id: int):
    course = CourseService.get_courses_by_id(course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return course