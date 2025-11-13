"""
Logging configuration for Diane API.
"""

import logging
import sys
from typing import Optional


def setup_logger(name: str = "diane_api", level: int = logging.INFO) -> logging.Logger:
    """
    Configure and return a logger instance.

    Args:
        name: Logger name
        level: Logging level (default: INFO)

    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(console_handler)

    return logger


def mask_sensitive_data(text: str, key_to_mask: Optional[str] = None) -> str:
    """
    Mask sensitive data in log messages.

    Args:
        text: Text to mask
        key_to_mask: Specific API key to mask

    Returns:
        Masked text
    """
    if not key_to_mask:
        return text

    # Mask API key if present in text
    if key_to_mask in text:
        masked_key = f"{key_to_mask[:7]}...***{key_to_mask[-4:]}"
        return text.replace(key_to_mask, masked_key)

    return text


# Create default logger instance
logger = setup_logger()
