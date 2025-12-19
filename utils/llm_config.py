"""
LLM Configuration utilities.

Provides canonical environment variable getters for LLM configuration.
Never logs or exposes secret values.
"""
import os
import logging
from typing import Optional


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
    key = os.getenv("OPENAI_API_KEY")
    
    # Log presence only (never the actual key)
    logger = logging.getLogger("LLM.Config")
    if key:
        logger.debug("OPENAI_API_KEY is present in environment")
    else:
        logger.warning("OPENAI_API_KEY is not set in environment")
    
    return key


def is_openai_configured() -> bool:
    """
    Check if OpenAI is properly configured without retrieving the key.
    
    Returns:
        True if OPENAI_API_KEY is present and non-empty, False otherwise.
    """
    key = os.getenv("OPENAI_API_KEY")
    return bool(key and key.strip())
