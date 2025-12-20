"""
LLM Configuration utilities.

Provides canonical environment variable getters for LLM configuration.
Never logs or exposes secret values.
"""
import os
import logging
from typing import Optional


def _get_env_openai_key() -> Optional[str]:
    """
    Read and sanitize the OpenAI API key from the current environment.
    
    Returns:
        The stripped API key string if present and non-empty, otherwise None.
    """
    raw = os.getenv("OPENAI_API_KEY")
    if raw is None:
        return None
    stripped = raw.strip()
    return stripped or None


def get_openai_api_key() -> Optional[str]:
    """
    Get the OpenAI API key from environment variable OPENAI_API_KEY.
    
    Returns:
        The API key string if present, None if missing.
        
    Note:
        - Does not log the key value
        - Does not raise exceptions
        - Only reads from OPENAI_API_KEY (not other variants)
    """
    key = _get_env_openai_key()
    
    # Log presence only (never the actual key)
    logger = logging.getLogger("LLM.Config")
    if key:
        logger.debug("OPENAI_API_KEY is present in environment")
    else:
        logger.warning("OPENAI_API_KEY is not set or empty in environment")
    
    return key


def is_openai_configured() -> bool:
    """
    Check if OpenAI is properly configured without retrieving the key.
    
    Returns:
        True if OPENAI_API_KEY is present and non-empty, False otherwise.
    """
    return _get_env_openai_key() is not None
