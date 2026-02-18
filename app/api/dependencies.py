from fastapi import HTTPException, status
from app.schemas.user_schema import UserRole
from app.services.user import UserService


#Dependency functions to check user roles and permissions
def get_user(user_id: int):
    user = UserService.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

#Dependency to check if the user is an admin
def is_admin_user(user_id: int):
    user = get_user(user_id)
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access needed")
    return user

#Dependency to check if the user is a student
def is_student_user(user_id: int):
    user = get_user(user_id)
    if user.role != UserRole.STUDENT:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Action allowed for students only")
    return user

