"""
Agent Configuration Module

This module handles all configuration settings for the agent including:
- Environment variable management
- Model configuration
- Database connections
- Logging setup
- Agent prompts and descriptions

The AgentConfig class serves as a centralized configuration object that can be
imported and used throughout the agent codebase.

Classes:
    AgentConfig: Main configuration dataclass containing all agent settings

Variables:
    settings: Global instance of AgentConfig for easy import and usage

Environment Variables:
    DATABASE_URL: Database connection string (optional)
    LOG_LEVEL: Logging level (default: INFO)
    MODEL_ID: LLM model identifier for the agent
    AGENT_INSTRUCTION: Custom agent prompt (overrides default)
    AGENT_DESCRIPTION: Custom agent description (overrides default)
"""

from dataclasses import dataclass, field
import os
import logging

from google.adk.agents.readonly_context import ReadonlyContext
from dotenv import load_dotenv

from adk_agent.logging_config import log_level
from adk_agent.prompts import get_agent_description, get_agent_instruction

load_dotenv()

logger = logging.getLogger(__name__)
logger.info("Logging is set up with level: %s", log_level)


@dataclass
class AgentConfig:
    """
    Configuration dataclass for agent settings and behavior.

    This class centralizes all configuration options for the agent, including
    database connections, logging levels, model settings, and prompt configuration.

    Attributes:
        database_url (str | None): Database connection URL from environment
        log_level (str): Logging verbosity level (default: INFO)
        model_id (str): Identifier for the LLM model to use

    Properties:
        agent_description (str): Brief description of agent capabilities
        agent_instruction (str): Complete system prompt for the agent

    Environment Variables:
        DATABASE_URL: Optional database connection string
        LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        MODEL_ID: Required - LLM model identifier
        AGENT_INSTRUCTION: Optional custom system prompt
        AGENT_DESCRIPTION: Optional custom agent description
    """

    # --> Common Settings
    # Database configuration (optional for stateless agents)
    database_url: str | None = field(default_factory=lambda: os.getenv("DATABASE_URL"))

    # Logging configuration
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    # <-- End of Common Settings

    # --> Agent Settings
    # Model configuration (required)
    model_id: str = field(default_factory=lambda: os.getenv("MODEL_ID"))
    # <-- End of Agent Settings

    # --> Agent Prompts and Descriptions
    @property
    def agent_description(self) -> str:
        """
        Get the agent's description from prompts module.

        Returns:
            str: Brief description of the agent's purpose and capabilities
        """
        return get_agent_description()

    @staticmethod
    def agent_instruction(context: ReadonlyContext) -> str:
        """
        Get the agent's system instruction/prompt with dynamic context.

        This method is static to allow passing context at runtime while
        maintaining clean configuration structure. The context includes
        user information and current date/time.

        Args:
            context (ReadonlyContext): Runtime context with state and user info

        Returns:
            str: Complete system instruction for the agent
        """
        return get_agent_instruction(context)

    # <-- End of Agent Instructions


# Global configuration instance
# Import this instance throughout the codebase: from config import settings
settings = AgentConfig()
