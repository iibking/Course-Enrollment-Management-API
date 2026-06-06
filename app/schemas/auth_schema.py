"""Auth-related schemas (the JWT response)."""
from pydantic import BaseModel


class Token(BaseModel):
    """Returned by the login endpoint."""
    access_token: str
    token_type: str = "bearer"