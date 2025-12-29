from fastapi import Header, HTTPException, status

from src.core.config import settings


def authorize(x_api_key: str = Header(None)):
    if not x_api_key or x_api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
