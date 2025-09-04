"""
Logging Configuration Module

This module sets up centralized logging configuration for the agent.
It configures log levels, formats, and output destinations based on environment variables.

Functions:
    setup_logging(): Configures the Python logging system with environment-based settings

Variables:
    log_level: The configured log level string (exported for use in other modules)

Environment Variables:
    LOG_LEVEL: Logging verbosity level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    LOG_FORMAT: Custom log message format string (optional)

Usage:
    This module is automatically imported by the config module to ensure logging
    is configured before any other components are initialized.
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
        str: The configured log level string for reference
        
    Environment Variables:
        LOG_LEVEL: Controls verbosity (DEBUG, INFO, WARNING, ERROR, CRITICAL)
                  Default: INFO
        LOG_FORMAT: Custom format string for log messages
                   Default: "%(asctime)s %(levelname)s [%(name)s] %(message)s"
    
    Examples:
        Basic usage:
        >>> log_level = setup_logging()
        >>> logger = logging.getLogger(__name__)
        >>> logger.info("Agent starting up...")
        
        With custom environment:
        >>> os.environ["LOG_LEVEL"] = "DEBUG"
        >>> os.environ["LOG_FORMAT"] = "%(levelname)s: %(message)s"
        >>> setup_logging()
    """
    # Get log level from environment with default fallback
    env_log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Get log format from environment with structured default
    log_format = os.getenv(
        "LOG_FORMAT", 
        "%(asctime)s %(levelname)s [%(name)s] %(message)s"
    )
    
    # Configure Python logging system
    logging.basicConfig(
        level=getattr(logging, env_log_level, logging.INFO), 
        format=log_format
    )
    
    return env_log_level


# Initialize logging configuration on module import
# This ensures logging is set up before any other modules use it
log_level = setup_logging()
