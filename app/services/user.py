from app.schemas.user_schema import UserCreate, User
from app.core.db import users 


class UserService:

#Creating users

    @staticmethod
    def create_user(user_in: UserCreate):
        user_dict = user_in.model_dump()
        user_id = len(users) + 1
       
        new_user = User(
            id=user_id,
            **user_dict
        )
        users[user_id] = new_user
        return new_user
    
    
#To retrieve all users

    @staticmethod
    def get_users():
        return list(users.values())

#To retrieve users by ID

    @staticmethod
    def get_user_by_id(user_id: int):
        return users.get(user_id)
