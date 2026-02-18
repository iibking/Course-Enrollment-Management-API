from fastapi import HTTPException, status
from app.schemas.enroll_schema import EnrollCreate, Enroll
from app.core.db import enrollments, users, courses


class EnrollService:

    @staticmethod
    def enroll_create(enroll_in: EnrollCreate):

    #Check if user exists    
        user = users.get(enroll_in.user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    #Check if course exists    
        course = courses.get(enroll_in.course_id)
        if not course:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
        

    #Check if user is already enrolled in the course
        for enrollment in enrollments.values():
            if enrollment.user_id == enroll_in.user_id and enrollment.course_id == enroll_in.course_id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already enrolled in this course")
               

        enroll_dict = enroll_in.model_dump()
        enroll_id = len(enrollments) + 1
        new_enrollment = Enroll(
            id=enroll_id,
            **enroll_dict
        )
        enrollments[enroll_id] = new_enrollment
        return new_enrollment
        
    
    #To retrieve all enrollments
    @staticmethod
    def get_enrollments():
        return list(enrollments.values())
    

    #To retrieve enrollments for a specific user
    @staticmethod
    def get_enrollments_by_user(user_id: int):
        return [enrollment for enrollment in enrollments.values() if enrollment.user_id == user_id]
    
    @staticmethod
    def get_enrollments_by_id(enroll_id: int):
        return enrollments.get(enroll_id)
    
    #To retrieve enrollments for a specific course
    @staticmethod
    def get_enrollment_by_course(course_id: int):
        return [enrollment for enrollment in enrollments.values() if enrollment.course_id == course_id]
    
    #To delete an enrollment
    @staticmethod
    def delete_enrollment(enroll_id: int):
        if enroll_id not in enrollments:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")
        del enrollments[enroll_id]
        return {"Message": "Enrollment deleted successfully"}
    