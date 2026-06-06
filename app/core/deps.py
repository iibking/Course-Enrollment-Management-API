from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator
from app.core.db_async import AsyncSessionLocal
from app.core.security import decode_token
from app.models.user import User
from app.repositories.user_repository import UserRepository


# Database session
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as db:
        yield db


# Authentication
# tokenUrl points at the login route so Swagger's "Authorize" button works.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db),
) -> User:
    
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exc
    except JWTError:
        # Covers invalid signature, malformed token, and expiry.
        raise credentials_exc

    user = await UserRepository.get_by_email(db, email)
    if user is None:
        raise credentials_exc
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Reject users whose account has been deactivated."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
        )
    return current_user


# Authorization (RBAC) 
def require_role(*roles: str):
    """
    Dependency factory: returns a dependency that allows the request only if
    the current (active) user has one of the given roles, else 403.
    """
    async def role_checker(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires role(s): {', '.join(roles)}",
            )
        return current_user
    return role_checker


# Concrete role guards used by the routers
require_admin = require_role("admin")
require_student = require_role("student")