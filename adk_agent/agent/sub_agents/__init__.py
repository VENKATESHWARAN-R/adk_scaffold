"""
Initialize sub-agents
This module initializes and configures sub-agents for the main agent.
"""

from .db_agent.config import DbAgentConfig
from .db_agent import agent

__all__ = [
    "DbAgentConfig",
    "agent",
]

DbAgentConfig().log_config()
