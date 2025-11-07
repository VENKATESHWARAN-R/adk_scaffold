"""
Logging Configuration Module

This module sets up centralized logging configuration for the agent.
Configures log levels and formats based on environment variables.

Functions:
    setup_logging(): Configures the Python logging system with environment-based settings

Environment Variables:
    LOG_LEVEL: Logging verbosity (DEBUG, INFO, WARNING, ERROR, CRITICAL) - default: INFO
    LOG_FORMAT: Custom log message format string - default: standard format

Usage:
    from logging_config import setup_logging
    setup_logging()

    import logging
    logger = logging.getLogger(__name__)
    logger.info("Agent starting...")

Best Practices:
    - Call setup_logging() once at application startup
    - Import this module in main.py or __init__.py
    - Use module-level loggers: logger = logging.getLogger(__name__)
    - Log levels: DEBUG for detailed info, INFO for general events,
      WARNING for concerning events, ERROR for errors, CRITICAL for severe issues
"""

import logging
import os


def setup_logging() -> str:
    """
    Configure the Python logging system with environment-based settings.

    Sets up logging level and format based on environment variables with
    sensible defaults. This function should be called once during application
    initialization.

    Returns:
        str: The configured log level string (e.g., 'INFO', 'DEBUG')

    Environment Variables:
        LOG_LEVEL: Controls verbosity (DEBUG, INFO, WARNING, ERROR, CRITICAL)
                  Default: INFO
        LOG_FORMAT: Custom format string for log messages
                   Default: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    Examples:
        Basic usage:
        >>> setup_logging()
        'INFO'
        >>> logger = logging.getLogger(__name__)
        >>> logger.info("Agent starting up...")

        With custom environment:
        >>> os.environ["LOG_LEVEL"] = "DEBUG"
        >>> os.environ["LOG_FORMAT"] = "%(levelname)s: %(message)s"
        >>> setup_logging()
        'DEBUG'
    """
    # Get log level from environment with default fallback
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    # Get log format from environment with structured default
    log_format = os.getenv(
        "LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Configure Python logging system
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format=log_format,
    )

    return log_level
