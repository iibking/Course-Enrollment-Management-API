from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user_schema import UserCreate


class UserRepository:
    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> User | None:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> User | None:
        """Used both for the uniqueness check and for loading the token's user."""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    @staticmethod
    async def create(db: AsyncSession, data: UserCreate) -> User:
        """Persist a new user, hashing the plaintext password before storing."""
        user = User(
            name=data.name,
            email=data.email,
            hashed_password=hash_password(data.password),
            role=data.role.value,
        )
        db.add(user)
        await db.flush()       # assigns the PK, commit happens in the route
        await db.refresh(user)
        return user