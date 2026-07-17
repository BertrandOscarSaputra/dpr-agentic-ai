"""API key authentication dependency."""

import logging

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from src.config import settings

logger = logging.getLogger(__name__)

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


async def require_api_key(
    api_key: str | None = Security(API_KEY_HEADER),
) -> str:
    """Validate the API key from the request header.

    If no API_KEYS are configured (empty list), authentication is
    disabled (development mode) and all requests are allowed.
    """
    if not settings.API_KEYS:
        return "dev"
    if api_key is None or api_key not in settings.API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
    logger.info("API key authenticated", extra={})
    return api_key
