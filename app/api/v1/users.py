from fastapi import APIRouter, HTTPException, status
from app.schemas.user_schema import UserCreate, User
from app.services.user import UserService



user_router = APIRouter()


#User creation
@user_router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate):
    return UserService.create_user(user_data)

#User retrieval
@user_router.get("/", response_model=list[User])
def get_users():
    return UserService.get_users()

#User retrieval by ID
@user_router.get("/{user_id}", response_model=User)
def get_user_by_id(user_id: int):
    user = UserService.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
