from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import verify_password, create_access_token
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreate

# Reused 401 header so clients know to send a Bearer token.
_AUTH_HEADERS = {"WWW-Authenticate": "Bearer"}


class AuthService:
    @staticmethod
    async def register(db: AsyncSession, data: UserCreate) -> User:
        if await UserRepository.get_by_email(db, data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )
        return await UserRepository.create(db, data)

    @staticmethod
    async def authenticate(db: AsyncSession, email: str, password: str) -> User:
        """Validate credentials and account status; return the user or raise 401."""
        user = await UserRepository.get_by_email(db, email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers=_AUTH_HEADERS,
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user",
                headers=_AUTH_HEADERS,
            )
        return user

    @staticmethod
    async def login(db: AsyncSession, email: str, password: str) -> str:
        """Return a signed JWT carrying the user's email (sub) and role."""
        user = await AuthService.authenticate(db, email, password)
        return create_access_token({"sub": user.email, "role": user.role})