"""Role-based access control decorators."""

from functools import wraps
from typing import List

from fastapi import Depends, HTTPException, status
from jose import JWTError

from app.security.jwt import decode_access_token


def get_current_user(token: str = Depends(lambda: None)) -> dict:
    """Get current authenticated user from token."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    return payload


def require_role(*roles: str):
    """Decorator to require specific roles."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: dict = Depends(get_current_user), **kwargs):
            user_role = current_user.get("role")
            if user_role not in roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized",
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator
