from fastapi import HTTPException, status
from app.schemas.course_schema import CourseCreate, CourseUpdate, Course
from app.core.db import courses


class CourseService:

#To retrieve all courses
    @staticmethod
    def get_courses():
        return list(courses.values())
    
#To retrieve a course by ID    
    @staticmethod
    def get_courses_by_id(course_id: int):
        return courses.get(course_id)
    
#Creating a course    
    @staticmethod
    def create_course(course_in: CourseCreate):
        course_dict = course_in.model_dump()

        for course in courses.values():
            if course.code == course_dict["code"]:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Code already assigned to another course")
            
        course_id = len(courses) + 1
        new_course = Course(
            id=course_id,
            **course_dict
        )
        courses[course_id] = new_course
        return new_course
    
#To update a course
    @staticmethod
    def update_course(course_id: int, course_in: CourseUpdate):
        course_dict = course_in.model_dump()
        existing_course = courses.get(course_id)

    #Check if the course exists    
        if not existing_course:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    #Check for code uniqueness    
        for course in courses.values():
            if course.code == course_dict["code"] and course.id != course_id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Code already assigned to another course")
        
        updated_course = Course(
            id=course_id,
            **course_dict
        )
        courses[course_id] = updated_course
        return updated_course
    

    #To delete a course
    @staticmethod
    def delete_course(course_id: int):
        if course_id not in courses:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
        del courses[course_id]
        return {"Message": "Course deleted successfully"}