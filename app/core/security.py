from datetime import datetime, timedelta, timezone
import bcrypt
from jose import jwt

from app.core.config import settings

# bcrypt only hashes the first 72 bytes of a password; we truncate explicitly
# so longer inputs don't raise.
_BCRYPT_MAX_BYTES = 72


# Passwords
def hash_password(plain: str) -> str:
    """Return a salted bcrypt hash of a plaintext password."""
    pw = plain.encode("utf-8")[:_BCRYPT_MAX_BYTES]
    return bcrypt.hashpw(pw, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Check a plaintext password against its stored bcrypt hash."""
    pw = plain.encode("utf-8")[:_BCRYPT_MAX_BYTES]
    return bcrypt.checkpw(pw, hashed.encode("utf-8"))


# JSON Web Tokens 
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])