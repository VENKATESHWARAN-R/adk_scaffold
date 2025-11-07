"""
Core Module - Centralized Configuration and Utilities

This module contains core configuration classes and utilities used throughout
the agent system, including base configuration, logging setup, and prompts.

Modules:
    base_config: Base configuration class for inheritance
    config: Main agent configuration
    prompts: Agent instruction and description templates
    logging_config: Logging setup and configuration

Usage:
    from adk_agent.core.config import settings
    from adk_agent.core.logging_config import setup_logging
    from adk_agent.core.base_config import BaseAgentConfig
"""

from .base_config import BaseAgentConfig
from .logging_config import setup_logging

__all__ = [
    "BaseAgentConfig",
    "setup_logging",
]
