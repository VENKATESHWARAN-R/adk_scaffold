"""
Application Initialization Module

This module initializes the application and exports the root_agent for use by the ADK framework.
Configuration logging is handled automatically by the settings classes.
"""

from .agent.config import AgentConfig
from .agent.agent import root_agent

__all__ = ["root_agent"]

# Log configuration once at application startup
AgentConfig().log_config()
