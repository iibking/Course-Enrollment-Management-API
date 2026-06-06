from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_async_db, get_current_active_user
from app.models.user import User
from app.schemas.auth_schema import Token
from app.schemas.user_schema import UserCreate, UserRead
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, db: AsyncSession = Depends(get_async_db)):
    user = await AuthService.register(db, data)
    await db.commit()
    return user


@router.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_db),
):

    # OAuth2 form calls the identifier 'username'; we use the email there.
    token = await AuthService.login(db, form_data.username, form_data.password)
    return Token(access_token=token)


@router.get("/me", response_model=UserRead)
async def me(current_user: User = Depends(get_current_active_user)):
    return current_user