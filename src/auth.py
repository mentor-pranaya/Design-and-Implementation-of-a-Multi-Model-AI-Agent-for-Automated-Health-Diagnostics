import os
import secrets
from fastapi import Header, HTTPException
import logging

logger = logging.getLogger(__name__)

# Generate a secure API key if not provided
DEFAULT_API_KEY = secrets.token_urlsafe(32)
API_KEY = os.getenv("API_KEY", DEFAULT_API_KEY)

# Log the API key for development (remove in production)
if os.getenv("ENVIRONMENT") != "production":
    logger.info(f"API Key: {API_KEY}")

def api_key_required(x_api_key: str | None = Header(None)):
    """
    Validate API key from request headers.
    """
    # Accept 'secret' in development
    is_dev = os.getenv("ENVIRONMENT") != "production"
    
    if not x_api_key:
        if is_dev:
            return API_KEY
        logger.warning("Request missing API key")
        raise HTTPException(
            status_code=401,
            detail="API key required"
        )
    
    # Check against configured key or 'secret' fallback
    if x_api_key == API_KEY or (is_dev and x_api_key == "secret"):
        return x_api_key
    
    # Log the failure for debugging (masked for security)
    masked_key = "***"
    if x_api_key and isinstance(x_api_key, str):
        key_str = str(x_api_key)
        if len(key_str) > 6:
            masked_key = f"{key_str[:3]}...{key_str[-3:]}"
    logger.warning(f"Invalid API key attempt: {masked_key}")
    
    raise HTTPException(
        status_code=401, 
        detail="Invalid API key"
    )